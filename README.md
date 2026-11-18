# Dashboards

Two interactive dashboard projects.

## 1. FlowTask Project Dashboard (static site)

`index.html` is a single self-contained page: KPIs, project progress, calendar, team, activity chart and a drag-and-drop Kanban board. No build step.

**Run locally:** double-click `index.html`.

**Publish with GitHub Pages:** repository **Settings → Pages → Deploy from a branch → `main` / root**. The site appears at `https://<your-username>.github.io/<repo-name>/`.

## 2. MarketPulse Business Analytics (Streamlit)

Folder: `marketpulse/`

- `app.py` is the Streamlit app (upload a CSV or Excel file, map columns, filter, click-to-drill, tabs for Overview, Explore and Data).
- `preview.html` is a standalone browser preview of the same design with sample data.

```bash
cd marketpulse
pip install -r requirements.txt
streamlit run app.py
```

Streamlit 1.35 or newer is needed for click-to-drill. The scatter trendline needs `statsmodels` (included in `requirements.txt`).

To deploy for free, use [Streamlit Community Cloud](https://streamlit.io/cloud) and point it at `marketpulse/app.py`.

## Notes

All data in both dashboards is synthetic sample data.
