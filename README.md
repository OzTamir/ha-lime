# Fluctuo Integration for Home Assistant

This integration allows you to monitor available Lime scooters near a specified location using the Fluctuo API.

## Features

- Displays the number of available Lime scooters
- Shows detailed information about the nearest scooter
- Lists all available scooters with their battery levels and distances

## Installation

1. Use HACS to install this custom component by adding this repository.
2. Restart Home Assistant.
3. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Fluctuo".

## Configuration

You will need to provide the following information:

- Fluctuo API Key
- Latitude and Longitude of the location you want to monitor
- Maximum distance (in meters) to search for scooters

## Usage

After setting up the integration, you can use the `sensor.lime_scooters_available` entity in your automations, scripts, and lovelace cards.

Example card (uses `auto-entities`, `fold-entity-row`, and `template-entity-row`)

```yaml
type: custom:auto-entities
card:
  type: entities
  title: Lime Scooters
  icon: mdi:scooter-electric
  show_header_toggle: false
filter:
  include:
    - entity_id: sensor.lime_scooters_available
entities:
  - entity: sensor.lime_scooters_available
    type: custom:fold-entity-row
    head:
      type: section
      label: Available Scooters
    items:
      - type: custom:template-entity-row
        entity: sensor.lime_scooters_available
        state: "{{ states('sensor.lime_scooters_available') }} Available"
        secondary: Last update {{ state_attr('sensor.lime_scooters_available', 'last_update') }}
      - type: conditional
        conditions:
          - entity: sensor.lime_scooters_available
            state: "0"
        row:
          type: section
          label: No scooters available
      - type: custom:fold-entity-row
        head:
          type: section
          label: Nearest Scooter
        items:
          - type: custom:template-entity-row
            state: "ID: {{ state_attr('sensor.lime_scooters_available', 'nearest_scooter').id }}"
          - type: custom:template-entity-row
            state: "Distance: {{ state_attr('sensor.lime_scooters_available', 'nearest_scooter').distance }}m"
          - type: custom:template-entity-row
            state: "Battery: {{ state_attr('sensor.lime_scooters_available', 'nearest_scooter').battery }}%"
          - type: custom:template-entity-row
            state: "Location: {{ state_attr('sensor.lime_scooters_available', 'nearest_scooter').lat }}, {{ state_attr('sensor.lime_scooters_available', 'nearest_scooter').lng }}"
      - type: custom:auto-entities
        card:
          type: entities
          show_header_toggle: false
        filter:
          template: >
            {{ state_attr('sensor.lime_scooters_available', 'available_vehicles') | default([]) }}
        card_param: entities
        variables:
          ulimit: 10
        sort:
          method: attribute
          attribute: distance
        card:
          type: custom:fold-entity-row
          head:
            type: section
            label: "Scooter {{ id }} ({{ distance }}m)"
          entities:
            - type: section
              label: "Battery: {{ battery }}%"
            - type: section
              label: "Location: {{ lat }}, {{ lng }}"
```

## Support

For bugs and feature requests, please open an issue on GitHub.
