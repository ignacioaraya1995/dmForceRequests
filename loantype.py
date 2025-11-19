#!/usr/bin/env python3
"""
Herramienta de Consolidación de Datos de Propiedades Inmobiliarias
Punto de entrada principal para la versión en español.

Esta herramienta consolida datos de propiedades de múltiples archivos CSV, aplica
filtrado basado en indicadores de dificultad y genera informes Excel formateados
para profesionales de bienes raíces.
"""

import time
from pathlib import Path

from src.utils.logger import get_logger
from src.utils.config import get_default_config
from src.data_processing.processor import DataProcessor, DataValidator
from src.file_operations.file_handler import (
    FileReader, DuplicateManager, ZipExtractor, FolderScanner
)
from src.file_operations.excel_formatter import ExcelFormatter, ReportGenerator
from src.ui.console_interface import ConsoleInterface, DataFilter, ProgressTracker


def main():
    """Pipeline principal de procesamiento."""
    start_time = time.time()

    # Inicializar configuración
    config = get_default_config(language='es', log_level='INFO')
    config.ensure_setup()

    # Inicializar logger
    logger = get_logger(__name__, log_level=config.log_level)
    logger.info("=" * 60)
    logger.info("Herramienta de Procesamiento de Datos Inmobiliarios - INICIADO")
    logger.info("=" * 60)

    # Inicializar componentes
    console = ConsoleInterface(config.language)
    progress = ProgressTracker()
    progress.set_total_steps(10)

    # Mostrar mensaje de bienvenida
    console.print_header("Herramienta de Consolidación de Datos Inmobiliarios")
    console.print_info("Iniciando proceso de consolidación y limpieza de datos...")

    try:
        # Paso 1: Obtener nombre del cliente
        client_name = console.get_client_name()
        console.print_success(f"Cliente seleccionado: {client_name}")
        progress.step_completed("Nombre del cliente recopilado")

        # Paso 2: Extraer archivos ZIP si están presentes
        logger.info("Verificando archivos ZIP para extraer...")
        zip_extractor = ZipExtractor()
        extracted_count = zip_extractor.extract_zip_files(config.paths.input_path)
        if extracted_count > 0:
            console.print_success(f"Extraídos {extracted_count} archivo(s) ZIP")
        progress.step_completed("Extracción de ZIP completada")

        # Paso 3: Escanear carpetas para procesar
        scanner = FolderScanner()
        folders = scanner.get_folders_to_process(
            config.paths.base_dir,
            [config.paths.input_folder]
        )

        if not folders:
            console.print_error("¡No se encontraron carpetas para procesar!")
            logger.error("No se encontraron carpetas válidas")
            return

        console.print_info(f"Se encontraron {len(folders)} carpeta(s) para procesar")
        progress.step_completed("Escaneo de carpetas completado")

        # Paso 4: Leer archivos CSV
        console.print_section("Leyendo Archivos CSV")
        file_reader = FileReader(config.processing)
        all_dataframes = []

        for folder in folders:
            logger.info(f"Procesando carpeta: {folder.name}")
            console.print_info(f"Procesando carpeta: {folder.name}")

            dfs = file_reader.read_csv_files_from_folder(folder)
            if dfs:
                all_dataframes.extend(dfs)
                console.print_success(f"Se leyeron {len(dfs)} archivo(s) CSV de {folder.name}")
            else:
                console.print_warning(f"No se leyeron archivos CSV de {folder.name}")

        if not all_dataframes:
            console.print_error("¡No se leyeron datos de los archivos CSV!")
            logger.error("No se cargaron dataframes")
            return

        progress.step_completed("Archivos CSV leídos")

        # Paso 5: Inicializar procesador de datos y consolidar
        console.print_section("Procesando Datos")
        processor = DataProcessor(config.columns, config.processing)
        validator = DataValidator()

        logger.info("Consolidando dataframes...")
        df = processor.consolidate_dataframes(all_dataframes)
        console.print_info(f"Se consolidaron {len(df):,} filas totales")
        progress.step_completed("Datos consolidados")

        # Paso 6: Limpieza y transformación de datos
        logger.info("Iniciando limpieza y transformación de datos...")

        df = processor.select_relevant_columns(df)
        console.print_info(f"Se seleccionaron {len(df.columns)} columnas relevantes")

        df = processor.clean_addresses(df)
        console.print_info(f"Se eliminaron filas con direcciones incompletas: {len(df):,} filas restantes")

        df = processor.calculate_distress_counter(df)
        console.print_info("Se calcularon puntuaciones de dificultad")

        df = processor.remove_duplicates(df)
        console.print_info(f"Se eliminaron duplicados: {len(df):,} filas restantes")

        df = processor.filter_top_by_distress(df)
        console.print_info(f"Se filtró el top {config.processing.percentage_to_retain:.0%}: {len(df):,} filas restantes")

        progress.step_completed("Limpieza de datos completada")

        # Paso 7: Reordenar y renombrar columnas
        logger.info("Reordenando y renombrando columnas...")
        df = processor.reorder_columns(df)
        df = processor.rename_columns(df)

        # Fusionar datos FIPS
        df = processor.merge_fips_data(df, config.paths.fips_file_path)

        df = processor.uppercase_columns(df)
        progress.step_completed("Formateo de columnas completado")

        # Paso 8: Filtrado interactivo
        console.print_section("Filtrado Interactivo")
        data_filter = DataFilter()
        df = data_filter.apply_interactive_filters(df)
        progress.step_completed("Filtrado interactivo completado")

        # Paso 9: Limpieza final
        console.print_section("Limpieza Final")
        df = processor.clean_ltv_values(df)
        df = processor.apply_title_case(df)
        console.print_info("Se aplicó formato final")
        progress.step_completed("Limpieza final completada")

        # Paso 10: Eliminar duplicados de archivos anteriores (opcional)
        console.print_section("Eliminación de Duplicados de Archivos Anteriores")
        if console.confirm_action("¿Desea eliminar propiedades listadas en archivos anteriores (carpeta 'Dupes')?"):
            dupe_manager = DuplicateManager()
            previous_addresses = dupe_manager.load_previous_addresses(config.paths.dupes_path)

            if previous_addresses:
                df, removed_count = processor.remove_previous_addresses(df, previous_addresses)
                console.print_success(f"Se eliminaron {removed_count:,} propiedades duplicadas")
            else:
                console.print_warning("No se encontraron direcciones anteriores para comparar")

        progress.step_completed("Eliminación de duplicados completada")

        # Validar datos finales
        if not validator.validate_dataframe(df, "DataFrame Final"):
            console.print_error("¡Validación de datos finales falló!")
            return

        # Paso 11: Guardar en Excel
        console.print_section("Guardando Resultados")
        excel_formatter = ExcelFormatter(config.excel, config.columns)
        output_file = excel_formatter.save_formatted_excel(
            df,
            config.paths.output_path,
            client_name
        )
        console.print_success(f"Archivo Excel guardado: {output_file.name}")
        logger.info(f"Archivo de salida guardado: {output_file}")

        # Paso 12: Generar informe resumen
        console.print_section("Resumen Final")
        report_generator = ReportGenerator()
        report_generator.print_summary_report(df)

        # Imprimir finalización
        elapsed_time = time.time() - start_time
        progress.print_summary(len(df), elapsed_time)

        console.print_success("¡Proceso completado con éxito!")
        logger.info(f"Procesamiento completado en {elapsed_time:.2f} segundos")
        logger.info("=" * 60)

    except KeyboardInterrupt:
        console.print_warning("\nProceso interrumpido por el usuario")
        logger.warning("Proceso interrumpido por el usuario")

    except Exception as e:
        console.print_error(f"Ocurrió un error: {e}")
        logger.error(f"Error fatal: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
