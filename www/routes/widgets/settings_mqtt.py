"""
disk2iso - MQTT Widget Settings Routes
Stellt die MQTT-Einstellungen bereit (Settings Widget)
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from flask import Blueprint, render_template, jsonify, request, g
from i18n import t

# Blueprint für MQTT Settings Widget
mqtt_settings_bp = Blueprint('mqtt_settings', __name__)

# Pfade
BASE_DIR = Path(__file__).parent.parent.parent.parent
SETTINGS_FILE = BASE_DIR / 'conf' / 'disk2iso.conf'


def get_mqtt_settings():
    """
    Liest MQTT-spezifische Konfiguration via libmqtt.sh CLI-Interface
    
    Returns:
        dict: MQTT-Konfiguration mit Keys:
              - mqtt_enabled (bool)
              - mqtt_broker (str)
              - mqtt_port (int)
              - mqtt_user (str)
              - mqtt_password (str)
    """
    try:
        # Rufe libmqtt.sh export-config auf
        libmqtt_path = BASE_DIR / 'lib' / 'libmqtt.sh'
        result = subprocess.run(
            [str(libmqtt_path), 'export-config'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            config = json.loads(result.stdout)
            # Konvertiere zu erwarteter Struktur (nur relevante Felder)
            return {
                "mqtt_enabled": config.get('mqtt_enabled', False),
                "mqtt_broker": config.get('mqtt_broker', ''),
                "mqtt_port": config.get('mqtt_port', 1883),
                "mqtt_user": config.get('mqtt_user', ''),
                "mqtt_password": config.get('mqtt_password', ''),
            }
        else:
            print(f"Fehler beim Lesen der MQTT-Konfiguration: {result.stderr}", file=sys.stderr)
            return {
                "mqtt_enabled": False,
                "mqtt_broker": "",
                "mqtt_port": 1883,
                "mqtt_user": "",
                "mqtt_password": "",
            }
    except Exception as e:
        print(f"Fehler beim Lesen der MQTT-Konfiguration: {e}", file=sys.stderr)
        return {
            "mqtt_enabled": False,
            "mqtt_broker": "",
            "mqtt_port": 1883,
            "mqtt_user": "",
            "mqtt_password": "",
        }


@mqtt_settings_bp.route('/api/widgets/mqtt/settings')
def api_mqtt_settings_widget():
    """
    Rendert das MQTT Settings Widget
    Zeigt MQTT-Einstellungen
    """
    config = get_mqtt_settings()
    
    # Rendere Widget-Template
    return render_template('widgets/settings_4x1_mqtt.html',
                         settings=config,
                         t=t)


@mqtt_settings_bp.route('/api/mqtt/save', methods=['POST'])
def api_mqtt_save():
    """
    Speichert MQTT-Konfiguration via libmqtt.sh CLI-Interface
    """
    try:
        data = request.get_json()
        
        # Validierung
        mqtt_enabled = data.get('mqtt_enabled', False)
        mqtt_broker = data.get('mqtt_broker', '')
        mqtt_port = int(data.get('mqtt_port', 1883))
        mqtt_user = data.get('mqtt_user', '')
        mqtt_password = data.get('mqtt_password', '')
        
        # Baue Konfigurations-Dict
        settings = {
            'mqtt_enabled': mqtt_enabled,
            'mqtt_broker': mqtt_broker,
            'mqtt_port': mqtt_port,
            'mqtt_user': mqtt_user,
            'mqtt_password': mqtt_password
        }
        
        # Rufe libmqtt.sh import-config auf
        libmqtt_path = BASE_DIR / 'lib' / 'libmqtt.sh'
        result = subprocess.run(
            [str(libmqtt_path), 'import-config'],
            input=json.dumps(config),
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            return jsonify({
                'success': True,
                'message': 'MQTT-Konfiguration gespeichert',
                'restart_required': True
            })
        else:
            return jsonify({
                'success': False,
                'error': result.stderr
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@mqtt_settings_bp.route('/api/mqtt/test', methods=['POST'])
def api_mqtt_test():
    """
    Testet MQTT-Verbindung via libmqtt.sh CLI-Interface
    """
    try:
        data = request.get_json()
        
        # Baue Test-Konfiguration
        settings = {
            'broker': data.get('broker', ''),
            'port': int(data.get('port', 1883)),
            'user': data.get('user', ''),
            'password': data.get('password', '')
        }
        
        # Rufe libmqtt.sh test-connection auf
        libmqtt_path = BASE_DIR / 'lib' / 'libmqtt.sh'
        result = subprocess.run(
            [str(libmqtt_path), 'test-connection'],
            input=json.dumps(config),
            capture_output=True,
            text=True,
            timeout=15
        )
        
        if result.returncode == 0:
            return jsonify({
                'success': True,
                'message': 'Verbindung erfolgreich'
            })
        else:
            return jsonify({
                'success': False,
                'error': result.stderr or 'Verbindung fehlgeschlagen'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


