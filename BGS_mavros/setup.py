from setuptools import find_packages, setup

package_name = 'BGS_mavros'

setup(
    name=package_name,
    version='0.0.0',
    packages=find_packages(include=[package_name]),  # Pastikan hanya paket utama yang diambil
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        ('share/' + package_name, ['launch/gazebo_sitl.launch.py']),
        ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='bagas',
    maintainer_email='bagaszpraa@gmail.com',
    description='Package for BGS MAVROS integration',
    license='TODO: License declaration',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'masterNode = BGS_mavros.masterNode:main',
            'bgs_mavros_2 = BGS_mavros.bgs_mavros_2:main',
        ],
    },
)
