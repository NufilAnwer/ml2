# DVC and DagsHub setup

Do these commands locally in the cloned repository. The DagsHub remote URL and credentials are account-specific; copy the exact remote URL shown in your DagsHub repository's DVC/Storage settings.

## 1. DVC toy exercise (small CSV)

Run this in a separate temporary directory so the toy data does not get mixed with the project dataset.

```bash
mkdir dvc-toy
cd dvc-toy
git init -b main
dvc init
mkdir toy
printf "id,value\n1,10\n2,20\n" > toy/sample.csv
dvc add toy/sample.csv
git add .gitignore .dvc toy/sample.csv.dvc
git commit -m "Track toy CSV version 1 with DVC"
# Change the data, then create version 2.
printf "id,value\n1,100\n2,200\n" > toy/sample.csv
dvc add toy/sample.csv
git add toy/sample.csv.dvc
git commit -m "Track toy CSV version 2 with DVC"
git log --oneline --all
# Restore the older pointer and materialize its data.
git checkout HEAD~1 -- toy/sample.csv.dvc
dvc checkout
```

Configure a remote using the URL copied from DagsHub. Example form only:

```bash
dvc remote add -d storage https://dagshub.com/OWNER/REPOSITORY.dvc
dvc remote modify --local storage auth basic
dvc remote modify --local storage user YOUR_DAGSHUB_USERNAME
dvc remote modify --local storage password YOUR_DAGSHUB_TOKEN
dvc push
rm toy/sample.csv
dvc pull
```

The remote URL above is a template, not a verified URL for your account. Never commit the token; `--local` stores authentication in local DVC configuration.

## 2. Track the VisionGuard dataset

Return to the VisionGuard repository root, activate its virtual environment and ensure the dataset is under `data/dataset/`.

```bash
dvc init
dvc remote add -d storage https://dagshub.com/OWNER/REPOSITORY.dvc
dvc remote modify --local storage auth basic
dvc remote modify --local storage user YOUR_DAGSHUB_USERNAME
dvc remote modify --local storage password YOUR_DAGSHUB_TOKEN
dvc add data/dataset
git add .dvc .gitignore data/dataset.dvc
git commit -m "Track VisionGuard dataset with DVC"
dvc push
```

Verify the objects in DagsHub storage. Commit the pointer file, not the image payload. A DVC pointer records the output path, content hash (MD5 or directory hash), and size; DVC stores the large payload in remote object storage. Git therefore versions the pointer while DVC transfers the actual data.

If DVC is already initialized, do not run `dvc init` again. Check `dvc status` first. If the remote is configured, do not add a duplicate remote.

## 3. DVC data version evidence

After adding a new or changed dataset snapshot:

```bash
dvc add data/dataset
git add data/dataset.dvc
git commit -m "Version updated dataset"
dvc push
```

To restore an earlier dataset version, check out the commit containing its pointer and run `dvc checkout`. Capture the terminal output and the DagsHub storage view for the report.
