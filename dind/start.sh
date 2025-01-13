set -e

# Start dockerd in the background with both unix and tcp endpoints
dockerd --host=unix:///var/run/docker.sock --host=tcp://0.0.0.0:2375 &
DIND_PID=$!

# Wait for Docker daemon to become available
until docker info >/dev/null 2>&1; do
    sleep 1
done

# Create the network inside dind
docker network create app-network || true

# Wait on the dockerd process
wait $DIND_PID