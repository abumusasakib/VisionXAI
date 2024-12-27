ARCH=$(uname -m)

if [ "$ARCH" = "x86_64" ]; then
  export BASE_IMAGE="tensorflow/tensorflow:2.8.0"
elif [ "$ARCH" = "aarch64" ]; then
  export BASE_IMAGE="armswdev/tensorflow-arm-neoverse:r22.04-tf-2.8.0-eigen"
else
  echo "Unsupported architecture: $ARCH"
  exit 1
fi

docker-compose up --build
