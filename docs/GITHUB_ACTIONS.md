# GitHub Actions for Publications Update

This repository includes an automated GitHub Actions workflow that keeps your publications and citations up-to-date by fetching data from Google Scholar.

## 🤖 Automated Workflow

The workflow is located at `.github/workflows/update-publications.yml` and performs the following tasks:

### **Triggers**
- **Daily Schedule**: Runs automatically every day at 6 AM UTC
- **Manual Trigger**: Can be triggered manually from the Actions tab
- **File Changes**: Runs when `data/publications.json` or `scripts/update_publications.py` is modified

### **What it does**
1. **Fetches Publications**: Runs the `update_publications.py` script to get latest publications from Google Scholar
2. **Updates Citations**: Retrieves current citation metrics (total citations, h-index, i10-index)
3. **Commits Changes**: Automatically commits and pushes any updates to the repository
4. **Updates Website**: Since this is a GitHub Pages site, changes are automatically deployed

## 🚀 Setup Instructions

### **1. Enable GitHub Actions**
- Go to your repository's **Actions** tab
- Click **Enable Actions** if not already enabled

### **2. Configure Repository Permissions**
- Go to **Settings** → **Actions** → **General**
- Under **Workflow permissions**, select **Read and write permissions**
- Check **Allow GitHub Actions to create and approve pull requests**

### **3. Update Google Scholar ID**
Edit the `scripts/update_publications.py` file and update the `scholar_id` variable:
```python
scholar_id = "YOUR_GOOGLE_SCHOLAR_ID"  # Replace with your actual ID
```

### **4. Test the Workflow**
- Go to **Actions** tab
- Select **Update Publications and Citations**
- Click **Run workflow** → **Run workflow**

## 📊 What Gets Updated

The workflow updates the following in `data/publications.json`:

### **Publications Data**
- Publication titles
- Authors
- Journals
- Years
- Citation counts
- Paper links

### **Citation Metrics**
- Total citations
- h-index
- i10-index
- Last updated timestamp

## 🔧 Manual Execution

You can run the script manually in several ways:

### **Local Execution**
```bash
# Interactive mode
python scripts/update_publications.py

# Automated mode (same as GitHub Actions)
python scripts/update_publications.py --auto-update
```

### **GitHub Actions Manual Trigger**
1. Go to **Actions** tab
2. Select **Update Publications and Citations**
3. Click **Run workflow**
4. Click **Run workflow** button

## 📈 Monitoring

### **Check Workflow Status**
- Go to **Actions** tab to see workflow runs
- Green checkmark = successful update
- Red X = failed (check logs for details)

### **View Recent Updates**
- Check the commit history for commits with message: `🤖 Auto-update publications and citations [skip ci]`
- Review `data/publications.json` for latest data

## ⚠️ Important Notes

### **Rate Limiting**
- Google Scholar has anti-bot measures
- The script includes delays and respectful headers
- If fetching fails, the workflow will still complete (no error)

### **Data Backup**
- The workflow only updates `data/publications.json`
- Your existing data is preserved and merged with new data
- Always review changes before they go live

### **Customization**
You can modify the workflow schedule by editing the cron expression in `.github/workflows/update-publications.yml`:
```yaml
schedule:
  - cron: '0 6 * * *'  # Daily at 6 AM UTC
```

## 🛠️ Troubleshooting

### **Workflow Fails**
1. Check the **Actions** tab for error logs
2. Verify your Google Scholar ID is correct
3. Ensure repository has proper permissions
4. Check if `requirements.txt` has all dependencies

### **No Updates**
1. Verify Google Scholar profile is public
2. Check if publications have changed recently
3. Review the workflow logs for any errors

### **Manual Override**
If automated updates aren't working, you can:
1. Run the script locally
2. Manually edit `data/publications.json`
3. Commit and push changes manually

## 📝 Example Workflow Run

```
✅ Found 15 publications
✅ Found metrics: {'total_citations': 299, 'h_index': 295, 'i10_index': 10}
🤖 Auto-update publications and citations [skip ci]
```

This workflow ensures your website always displays the most current publication and citation data automatically! 🎯 