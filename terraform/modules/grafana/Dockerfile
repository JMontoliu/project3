FROM grafana/grafana:latest

USER root

# Instalar el plugin oficial de BigQuery
RUN grafana-cli plugins install grafana-bigquery-datasource

COPY provisioning /etc/docker/provisioning
COPY dashboards /etc/docker/provisioning/dashboards