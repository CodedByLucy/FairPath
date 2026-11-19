# FairPath: Bias in AI Systems

CA-3 Mini Project, Group 1. An AI job screening app with an admin console that measures and reduces gender and race bias.

## Team

| Name | Register number | GitHub |
|---|---|---|
| Bijil B Maniyat | 20211CCS0162 | [@CodedByLucy](https://github.com/CodedByLucy) |
| Rajith S V | 20241CCS0092 | [@Rajithsv52-lang](https://github.com/Rajithsv52-lang) |
| Chethan M | 20241CCS0100 | [@m-chethan-security](https://github.com/m-chethan-security) |
| Dinesh Kumar | 20251LCC3008 | [@motorhead2410-cmyk](https://github.com/motorhead2410-cmyk) |
| Mohammed Farhaan Zaheer | 20241CCS0068 | |
| Umar Rizwan | 20231CCS0046 | |

## What is inside

| Path | Purpose |
|---|---|
| `app.py` | Starts the app and the page navigation |
| `engine.py` | Loads data, trains the three models (historical, standard, fair), stores applications, runs the bias checks |
| `ui.py` | Icons, navigation bar, tiles, charts, ethics box |
| `style.css` | Dark visual design |
| `views/home.py` | Landing page with the bias numbers from the data |
| `views/apply.py` | Job application form for normal users |
| `views/admin.py` | Admin console with fairness metrics |
| `prepare_data.py` | Builds `data/adult.csv` from the raw downloads |
| `data/adult.csv` | Training data used by the app (45,222 rows) |
| `data/raw/` | Original downloads, kept local only (not in the repository) |
| `.streamlit/config.toml` | Dark theme settings |

## 1. Install

You need Python 3.10 or later.

```bash
cd fairpath
python3 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Prepare the data (only if `data/adult.csv` is missing)

```bash
python prepare_data.py
```

It reads `data/raw/uci_adult.zip` (downloads it if missing), joins the UCI train and test files, removes rows with missing values and writes `data/adult.csv`. If `data/raw/openml_adult.arff` is present it also checks that OpenML has the same records.

Expected output:

```
Wrote 45,222 rows to .../data/adult.csv
OpenML cross check: identical records
```

## 3. Run

```bash
streamlit run app.py
```

The browser opens at http://localhost:8501. The models train on first load, which takes a few seconds.

## 4. Use it

1. **Home**: shows how biased the training data is.
2. **Apply**: fill the form and submit. The AI shows a match score and whether you are shortlisted.
3. **Admin**: password `admin123`.
   - Click **Add 20 samples** to fill the console with real applicants from the test set.
   - Read the **fairness ratio** (80% rule) and the **gender flip test**.
   - Switch **Screening model** to **Fair model (blind)** and watch the flip test drop to zero.
   - Move the **shortlist cut off** slider to see how the rates change.

Applications live in server memory. They are shared by all visitors and cleared when the app restarts.

## 5. Deploy on Streamlit Community Cloud

1. Use the public repository https://github.com/CodedByLucy/FairPath.
2. Upload everything in this folder, including the hidden `.streamlit` folder.
3. Go to share.streamlit.io, click **New app**, pick the repository, branch `main`, file `app.py`, then **Deploy**.
4. Optional: in **Advanced settings, Secrets**, add `ADMIN_PASSWORD = "your-password"` to change the admin password.
5. Open the link once before the demo, since free apps sleep when unused.

## Data source

UCI Machine Learning Repository, Adult (Census Income) dataset, https://archive.ics.uci.edu/dataset/2/adult. The same records are on OpenML (https://www.openml.org/d/1590) and Kaggle (https://www.kaggle.com/datasets/uciml/adult-census-income).
