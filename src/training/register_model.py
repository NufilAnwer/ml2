"""Register two trained run artifacts as versions and assign champion alias."""
import argparse
import mlflow
from dotenv import load_dotenv

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model-name", default="VisionGuard")
    parser.add_argument("--run-id-v1", required=True)
    parser.add_argument("--run-id-v2", required=True)
    args = parser.parse_args()
    load_dotenv()
    client = mlflow.MlflowClient()
    for run_id in [args.run_id_v1, args.run_id_v2]:
        model_uri = f"runs:/{run_id}/model_files"
        version = mlflow.register_model(model_uri, args.model_name)
        print("Registered version:", version.version, "from run:", run_id)
    versions = client.search_model_versions(f"name='{args.model_name}'")
    newest = max(versions, key=lambda item: int(item.version))
    client.set_registered_model_alias(args.model_name, "champion", newest.version)
    print(f"Alias champion -> {args.model_name} version {newest.version}")

if __name__ == "__main__":
    main()
