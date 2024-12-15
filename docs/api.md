# Smart Service API Documentation

## Overview
This service provides gRPC endpoints for managing smart devices and services.

## Endpoints

### CreateModel
Creates a new smart model.
```protobuf
rpc CreateModel (CreateModelRequest) returns (SmartModel)
```

### ListModels
Lists all models with filtering options.
```protobuf
rpc ListModels (ListModelsRequest) returns (ListModelsResponse)
```

### AddFeature
Adds a new feature to an existing model.
```protobuf
rpc AddFeature (AddFeatureRequest) returns (SmartFeature)
```

## Data Types

### SmartModel
```protobuf
message SmartModel {
    string id = 1;
    string name = 2;
    string type = 3;
    string category = 4;
    string description = 5;
}
```

### SmartFeature
```protobuf
message SmartFeature {
    string id = 1;
    string model_id = 2;
    string name = 3;
    string description = 4;
    string function_type = 5;
}
```

## Example Usage
See `src/client.py` for example usage of each endpoint.