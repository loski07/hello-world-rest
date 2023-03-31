# hello-world-rest
## Abstract
Dummy service that implements a [REST API with a bunch of endpoints](hello_world_rest/README.md) that is used to
describe how to do no downtime blue/green deployments and have monitoring elements to confirm that the service was not
down during the deployment.

## Components included
- Python App
- MongoDB
- HAProxy
- Prometheus
- Prometheus Alertmanager
- Blackbox Exporter
- Grafana

## How to use the project
We include a `docker-compose` file that will allow you to do the deployments in a local machine. It contains the
configuration needed to successfully deploy all the components specified in the previous section that will simulate, in
one single machine, a cloud environment. The HAProxy balancer would simulate an Application Load Balancer that could be
in front of the 2 API services needed for the implementation of the zero downtime deployments. These 2 API services are
created also as docker containers simulating EC2 instances. We have an initial `docker-compose` profile, that will build
and start the balancer, the blue instance of the REST API, the database and all the monitoring elements. In order to
perform a zero-downtime deployment, we could follow the script below:
```shell
# Deploy the service (only the blue instance)
docker-compose up --build --force-recreate --profile initial
# Modify here the source code if you need
docker-compose up --build --force-recreate -d app-green
docker-compose down -d app-blue
# You can verify in prometheus or in the grafana dashboard we provide (if you import it) that the service was reachable
# all the time by querying prometheus for: 'probe_success{job="blackbox", instance="http://balancer:80/isAlive"}'

```

## Deploy diagram
There are multiple ways we could architect a cloud solution for this deployment:
- Using k8s: this might be the easiest way. We just need to create a Deployment, Service and Ingres for the Python API
  and another Deployment and service for the MongoDB instance. All those elements can be created using Helm Charts,
  Jsonnet, Kustomize or pure k8s manifest definition. We can configure the Python API deployment to perform
  rolling updates so, in order to make a zero-downtime deployment we just need to push a new image to the
  registry and modify the image `kubectl set image deployment python-api-deployment python-api-container=hello-world-rest-app:latest`
- Using EC2: We can simply provision EC2 instances (with docker installed) for the Python APP and the MongoDB and
  include the instances for the Python APP in the balancing pool of an Application Load Balancer. The zero-downtime
  deployment can be done by creating a new EC2 instance with the app deployed on it, including it in the pool of the 
  balancer and removing the old instances. We can use `Terraform` for creating the network layout and each individual
  EC2 instance. In the image below, you can see an ![AWS diagram](docs/AWS-diagram.png) for this alternative.

Both solutions can be orchestrated with a CD pipeline of the multiple solutions you can find in the market (Jenkins,
Spinnaker, GitHub Actions,...) 

# Future work
- Add Grafana Loki for log management
- Instrument the application (APM)
- Create Helm Chart
- Add Spinnaker deployment configuration
