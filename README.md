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

## Support

For bugs and feature requests, please open an issue on GitHub.
