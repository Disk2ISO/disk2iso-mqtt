/**
 * Dependencies Widget (4x1) - MQTT
 * Zeigt MQTT spezifische Tools (mosquitto clients)
 * Version: 1.0.0
 */

function loadMqttDependencies() {
    fetch('/api/widgets/mqtt/dependencies')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.software) {
                updateMqttDependencies(data.software);
            }
        })
        .catch(error => {
            console.error('Fehler beim Laden der MQTT-Dependencies:', error);
            showMqttDependenciesError();
        });
}

function updateMqttDependencies(softwareList) {
    const tbody = document.getElementById('mqtt-dependencies-tbody');
    if (!tbody) return;
    
    // MQTT-spezifische Tools (aus libmqtt.ini [dependencies])
    const mqttTools = [
        { name: 'mosquitto_pub', display_name: 'Mosquitto Publisher' }
    ];
    
    let html = '';
    
    mqttTools.forEach(tool => {
        const software = softwareList.find(s => s.name === tool.name);
        if (software) {
            html += renderSoftwareRow(tool.display_name, software);
        }
    });
    
    if (html === '') {
        html = '<tr><td colspan="4" style="text-align: center; padding: 20px; color: #999;">Keine Informationen verfügbar</td></tr>';
    }
    
    tbody.innerHTML = html;
}

function showMqttDependenciesError() {
    const tbody = document.getElementById('mqtt-dependencies-tbody');
    if (!tbody) return;
    
    tbody.innerHTML = '<tr><td colspan="4" style="text-align: center; padding: 20px; color: #e53e3e;">Fehler beim Laden</td></tr>';
}

// Auto-Load
if (document.getElementById('mqtt-dependencies-widget')) {
    loadMqttDependencies();
}
