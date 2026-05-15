from databricks import sql
import configparser


class DatabricksClient:

    def __init__(self, config_file='config.properties'):
        config = configparser.ConfigParser()
        config.read(config_file)

        # configparser loads .properties into DEFAULT section
        cfg = {k: v for k, v in config.items('DEFAULT')}

        self.server_hostname = cfg.get('server_hostname')
        self.http_path = cfg.get('http_path')
        self.access_token = cfg.get('access_token')

    def getSdkInitEventsByInstallIdAndDate(self, installId, eventType):

        query = f"""
        SELECT 
            (CONCAT(DATE_FORMAT(COALESCE(event_created_time_ntp, event_created_time_device), 'yyyy-MM-dd HH:mm:ss'), '.', 
            RPAD(SUBSTRING(COALESCE(event_created_time_ntp, event_created_time_device), 21, 6), 6, '0'))) 
            AS combined_created_time_microsecond,
            event_created_time_ntp,
            event_created_time_device,
            event_type,
            game_id,
            device_platform,
            app_version,
            install_id,
            install_store_country,
            install_mode,
            install_name,
            install_bundle_id,
            install_server_country,
            player_id_type,
            player_id_value,
            previous_app_version,
            device_model,
            device_os,
            device_os_version,
            device_screen_dpi,
            device_screen_width,
            device_screen_height,
            device_system_memory,
            device_processor_type,
            app_instance_id,
            app_session_id,
            event_send_context,
            (CASE WHEN sdk_init_success THEN 'Yes' ELSE 'No' END) AS sdk_init_success,
            sdk_init_stage,
            kwsdk_version,
            connection_type,
            session_context,
            ad_placement,
            ad_unique_id,
            ad_mediator,
            ad_revenue,
            ad_auction_instance,
            ad_network,
            ad_auction_type,
            ad_format,
            ad_creative_id,
            ad_request_id,
            (CASE WHEN ad_show THEN 'Yes' ELSE 'No' END) AS ad_show,
            ad_no_show_context,
            ad_no_load_error_code,
            (CONCAT(DATE_FORMAT(ingestion_time, 'yyyy-MM-dd HH:mm:ss'), '.', 
            RPAD(SUBSTRING(ingestion_time, 21, 6), 6, '0'))) AS ingestion_microsecond,
            level_value,
            level_id,
            stage_value,
            stage_id,
            attempt_id,
            continue_context,
            screen_name,
            screen_transition_id,
            currencies_spent,
            currencies_earned,
            currencies_held
        FROM prd_mobile.kwalee_events_bronze.stg_tester_events
        WHERE install_id = '{installId}'
        AND event_type = '{eventType}'
        ORDER BY combined_created_time_microsecond ASC
        LIMIT 5000
        """

        try:
            # Connect to Databricks
            with sql.connect(
                server_hostname=self.server_hostname,
                http_path=self.http_path,
                access_token=self.access_token
            ) as connection:

                with connection.cursor() as cursor:
                    cursor.execute(query)
                    rows = cursor.fetchall()

                    # Column headers
                    columns = [col[0] for col in cursor.description]

                    # Format results
                    output = ""
                    for row in rows:
                        for col_name, value in zip(columns, row):
                            output += f"{col_name}: {value}\n"
                        output += "-" * 60 + "\n"

                    return output if output else "No records found."

        except Exception as e:
            return f"Error executing query: {str(e)}"
