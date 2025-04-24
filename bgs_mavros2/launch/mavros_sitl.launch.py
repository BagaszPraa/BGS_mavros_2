from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterFile


def generate_launch_description():
    # LaunchConfigurations untuk digunakan dalam Node
    fcu_url = LaunchConfiguration('fcu_url')
    gcs_url = LaunchConfiguration('gcs_url')
    tgt_system = LaunchConfiguration('tgt_system')
    tgt_component = LaunchConfiguration('tgt_component')
    pluginlists_yaml = LaunchConfiguration('pluginlists_yaml')
    config_yaml = LaunchConfiguration('config_yaml')
    log_output = LaunchConfiguration('log_output')
    fcu_protocol = LaunchConfiguration('fcu_protocol')
    respawn_mavros = LaunchConfiguration('respawn_mavros')
    namespace = LaunchConfiguration('namespace')

    # Path relatif ke file konfigurasi
    default_pluginlists_path = PathJoinSubstitution([
        FindPackageShare('mavros'),
        'launch',
        'apm_pluginlists.yaml'
    ])

    default_config_path = PathJoinSubstitution([
        FindPackageShare('mavros'),
        'launch',
        'apm_config.yaml'
    ])

    return LaunchDescription([
        DeclareLaunchArgument('fcu_url', default_value='udp://127.0.0.1:14550@14550',
                              description='URL ke flight controller'),
        DeclareLaunchArgument('gcs_url', default_value='',
                              description='URL ke ground control station'),
        DeclareLaunchArgument('tgt_system', default_value='1',
                              description='Target system ID'),
        DeclareLaunchArgument('tgt_component', default_value='1',
                              description='Target component ID'),
        DeclareLaunchArgument('pluginlists_yaml', default_value=default_pluginlists_path,
                              description='Path ke pluginlists YAML'),
        DeclareLaunchArgument('config_yaml', default_value=default_config_path,
                              description='Path ke konfigurasi MAVROS YAML'),
        DeclareLaunchArgument('log_output', default_value='screen',
                              description='Tempat log akan ditampilkan'),
        DeclareLaunchArgument('fcu_protocol', default_value='v2.0',
                              description='Versi protokol MAVLink'),
        DeclareLaunchArgument('respawn_mavros', default_value='false',
                              description='Respawn MAVROS jika node crash'),
        DeclareLaunchArgument('namespace', default_value='mavros',
                              description='Namespace untuk node MAVROS'),

        Node(
            package='mavros',
            executable='mavros_node',
            namespace=namespace,
            output=log_output,
            parameters=[
                {'fcu_url': fcu_url},
                {'gcs_url': gcs_url},
                {'tgt_system': tgt_system},
                {'tgt_component': tgt_component},
                {'fcu_protocol': fcu_protocol},
                ParameterFile(pluginlists_yaml, allow_substs=True),
                ParameterFile(config_yaml, allow_substs=True)
            ]
        )
    ])
