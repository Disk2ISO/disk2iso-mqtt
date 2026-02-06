"""
disk2iso - MQTT Module Routes
Blueprint fÃ¼r alle MQTT-spezifischen API-Endpoints
"""

from flask import Blueprint, render_template, request, jsonify, g
from datetime import datetime
import subprocess
import json
import sys
from pathlib import Path

# Blueprint Definition
mqtt_bp = Blueprint('mqtt', __name__)

# Pfade
BASE_DIR = Path(__file__).parent.parent.parent
SETTINGS_FILE = BASE_DIR / 'conf' / 'disk2iso.conf'


def get_mqtt_config():
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


def get_settings():
    """Legacy-Wrapper fÃ¼r KompatibilitÃ¤t mit bestehendem Code"""
    return get_mqtt_config()


@mqtt_bp.route('/api/mqtt/widget')
def api_mqtt_widget():
    """
    Rendert das MQTT Service Status Widget
    Zeigt aktuellen MQTT-Service Status
    """
    settings = get_settings()
    
    # MQTT-Status basierend auf config.sh
    if settings['mqtt_enabled']:
        mqtt_status = {'status': 'active', 'running': True}
    else:
        mqtt_status = {'status': 'inactive', 'running': False}
    
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Rendere Widget-Template
    return render_template('widgets/status_2x1_mqtt.html',
        mqtt_status=mqtt_status,
        current_time=current_time,
        t=g.t  # Translations
    )


@mqtt_bp.route('/api/widgets/mqtt/settings')
def api_mqtt_settings_widget():
    """
    Rendert das MQTT Settings Widget
    Formular fÃ¼r MQTT-Einstellungen
    """
    settings = get_settings()
    
    return render_template('widgets/mqtt_widget_4x1_settings.html',
        config=config,
        t=g.t  # Translations
    )


@mqtt_bp.route('/api/mqtt/test', methods=['POST'])
def api_mqtt_test():
    """
    Testet MQTT-Verbindung via libmqtt.sh CLI-Interface
    
    Request JSON:
    {
        "broker": "192.168.20.10",
        "port": 1883,
        "user": "username",      # optional
        "password": "password"   # optional
    }
    
    Response JSON:
    {
        "success": true/false,
        "error": "error message" # nur bei Fehler
    }
    """
    try:
        data = request.get_json()
        
        # Rufe libmqtt.sh test-connection auf (JSON via stdin)
        libmqtt_path = BASE_DIR / 'lib' / 'libmqtt.sh'
        result = subprocess.run(
            [str(libmqtt_path), 'test-connection'],
            input=json.dumps(data),
            capture_output=True,
            text=True,
            timeout=5
        )
        
        # Parse JSON-Response
        try:
            response = json.loads(result.stdout)
            return jsonify(response)
        except json.JSONDecodeError:
            return jsonify({'success': False, 'error': 'UngÃ¼ltige Response vom MQTT-Test'}), 500
            
    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'error': 'Verbindungs-Timeout (5s)'}), 408
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@mqtt_bp.route('/api/mqtt/status')
def api_mqtt_status():
    """
    Gibt aktuellen MQTT-Status als JSON zurÃ¼ck
    
    Response JSON:
    {
        "enabled": true/false,
        "broker": "192.168.20.10",
        "port": 1883,
        "authenticated": true/false,
        "status": "active"/"inactive"
    }
    """
    settings = get_settings()
    
    return jsonify({
        'enabled': settings['mqtt_enabled'],
        'broker': settings['mqtt_broker'],
        'port': settings['mqtt_port'],
        'authenticated': bool(settings['mqtt_user']),
        'status': 'active' if settings['mqtt_enabled'] else 'inactive'
    })


@mqtt_bp.route('/api/mqtt/save', methods=['POST'])
def api_mqtt_save():
    """
    Speichert MQTT-Konfiguration via libmqtt.sh CLI-Interface (Auto-Save)
    
    Request JSON:
    {
        "mqtt_enabled": true/false,
        "mqtt_broker": "192.168.20.10",
        "mqtt_port": 1883,
        "mqtt_user": "username",      # optional
        "mqtt_password": "password"   # optional
    }
    
    Response JSON:
    {
        "success": true/false,
        "restart_required": true/false,
        "error": "error message" # nur bei Fehler
    }
    """
    try:
        data = request.get_json()
        
        # Rufe libmqtt.sh update-config auf (JSON via stdin)
        libmqtt_path = BASE_DIR / 'lib' / 'libmqtt.sh'
        result = subprocess.run(
            [str(libmqtt_path), 'update-config'],
            input=json.dumps(data),
            capture_output=True,
            text=True,
            timeout=5
        )
        
        # Parse JSON-Response
        try:
            response = json.loads(result.stdout)
            return jsonify(response)
        except json.JSONDecodeError:
            return jsonify({'success': False, 'error': 'UngÃ¼ltige Response vom Config-Update'}), 500
        
    except subprocess.TimeoutExpired:
        return jsonify({'success': False, 'error': 'Timeout beim Speichern'}), 408
    except Exception as e:
        print(f"Fehler beim Speichern der MQTT-Konfiguration: {e}", file=sys.stderr)
        return jsonify({'success': False, 'error': str(e)}), 500

