#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
============================================================================
disk2iso - Status Widget (2x1) - MQTT
============================================================================
Filepath: www/routes/widgets/status_mqtt.py

Beschreibung:
    Flask Blueprint für MQTT Service Status Widget
    - Zeigt MQTT-Verbindungsstatus und Broker-Informationen
    - Nutzt mqtt_get_status() aus libmqtt.sh
============================================================================
"""

from flask import Blueprint, jsonify
import subprocess
import json
import os
from datetime import datetime

# Blueprint erstellen
status_mqtt_bp = Blueprint(
    'status_mqtt',
    __name__,
    url_prefix='/api/widgets/mqtt'
)

# Pfade
INSTALL_DIR = os.environ.get('DISK2ISO_INSTALL_DIR', '/opt/disk2iso')


def get_mqtt_status():
    """
    Ruft MQTT-Status via Bash-Funktion ab
    Nutzt mqtt_get_status() aus libmqtt.sh
    """
    try:
        result = subprocess.run(
            ['bash', '-c', f'source {INSTALL_DIR}/lib/liblogging.sh && source {INSTALL_DIR}/lib/libsettings.sh && source {INSTALL_DIR}/lib/libmqtt.sh && mqtt_get_status'],
            capture_output=True, text=True, timeout=5
        )
        
        if result.returncode == 0:
            return json.loads(result.stdout.strip())
        return {
            'status': 'unknown',
            'connected': False,
            'enabled': False
        }
    except Exception as e:
        print(f"Fehler beim Abrufen des MQTT-Status: {e}")
        return {
            'status': 'error',
            'connected': False,
            'enabled': False,
            'error': str(e)
        }


@status_mqtt_bp.route('/status')
def api_mqtt_status():
    """
    GET /api/widgets/mqtt/status
    Liefert aktuellen MQTT-Verbindungsstatus
    """
    mqtt_status = get_mqtt_status()
    
    return jsonify({
        'success': True,
        'service': 'mqtt',
        **mqtt_status,
        'timestamp': datetime.now().isoformat()
    })


def register_blueprint(app):
    """Registriert Blueprint in Flask-App"""
    app.register_blueprint(status_mqtt_bp)
