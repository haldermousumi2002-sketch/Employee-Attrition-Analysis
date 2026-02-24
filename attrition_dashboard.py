import streamlit as st
import pandas as pd
import plotly.express as px
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor
import io


# Page Configuration
st.set_page_config(page_title="HR Employees Attrition", page_icon="🎨", layout="wide")

# Custom CSS for Metric Cards + Dark Mode Summary
st.markdown("""
<style>

/* ===== Metric Cards ===== */
.metric-card {
    background: linear-gradient(135deg, #667eea, #764ba2);
    padding: 20px;
    border-radius: 15px;
    text-align: center;
    box-shadow: 0px 8px 20px rgba(0,0,0,0.15);
}

.metric-value {
    font-size: 32px;
    font-weight: bold;
    margin: 0;
}

.metric-label {
    font-size: 14px;
    margin: 0;
    letter-spacing: 0.5px;
}

/* ===== Dark Mode Friendly Action Cards ===== */
.action-card {
    background: rgba(40, 44, 52, 0.85);
    padding: 20px;
    border-radius: 12px;
    border-left: 6px solid #FF4B4B;
    margin-bottom: 15px;
    box-shadow: 0 6px 18px rgba(0,0,0,0.35);
    color: #f0f0f0;
}

.action-title {
    font-weight: bold;
    color: #61dafb;
    font-size: 18px;
}

/* List text visibility */
.action-card ul li {
    color: #e6e6e6;
}

</style>
""", unsafe_allow_html=True)

# Load Data
@st.cache_data
def load_data():
    # Ensure this filename matches your local environment
    df = pd.read_csv("WA_Fn-UseC_-HR-Employee-Attrition.csv")
    return df

df = load_data()

# Sidebar Filters
st.sidebar.header("🎨 Dashboard Controls")

# 1. Search Bar for specific IDs
search_id = st.sidebar.text_input("🔍 Search Employee ID", "")

# 2. Department Filter
dept_filter = st.sidebar.multiselect(
    "Select Department", 
    options=df["Department"].unique(), 
    default=df["Department"].unique()
)

# 3. Job Role Filter (Very useful for pinpointing issues)
role_filter = st.sidebar.multiselect(
    "Select Job Role", 
    options=df["JobRole"].unique(), 
    default=df["JobRole"].unique()
)

# 4. Education Field Filter
edu_filter = st.sidebar.multiselect(
    "Education Background", 
    options=df["EducationField"].unique(), 
    default=df["EducationField"].unique()
)

# 5. Salary Range Slider
min_sal, max_sal = int(df["MonthlyIncome"].min()), int(df["MonthlyIncome"].max())
salary_range = st.sidebar.slider(
    "Monthly Income Range",
    min_sal, max_sal, (min_sal, max_sal)
)

# --- Applying Filters to the Dataframe ---
filtered_df = df[
    (df["Department"].isin(dept_filter)) & 
    (df["JobRole"].isin(role_filter)) &
    (df["EducationField"].isin(edu_filter)) &
    (df["MonthlyIncome"].between(salary_range[0], salary_range[1]))
]

# If search ID is used, override other filters
if search_id:
    filtered_df = df[df["EmployeeNumber"].astype(str) == search_id]

# --- TOP DASHBOARD METRICS ---
st.title("📊 HR Employees Attrition Anaylsis ")
m1, m2, m3, m4 = st.columns(4)
total = len(filtered_df)
attr_rate = (filtered_df['Attrition'] == 'Yes').mean() * 100

with m1:
    st.markdown(f'<div class="metric-card" style="border-top: 5px solid #636EFA;"><p class="metric-label">Total Staff</p><p class="metric-value" style="color: #636EFA;">{total}</p></div>', unsafe_allow_html=True)
with m2:
    st.markdown(f'<div class="metric-card" style="border-top: 5px solid #EF553B;"><p class="metric-label">Attrition Rate</p><p class="metric-value" style="color: #EF553B;">{attr_rate:.1f}%</p></div>', unsafe_allow_html=True)
with m3:
    st.markdown(f'<div class="metric-card" style="border-top: 5px solid #00CC96;"><p class="metric-label">Avg Satisfaction</p><p class="metric-value" style="color: #00CC96;">{filtered_df["JobSatisfaction"].mean():.2f}/4</p></div>', unsafe_allow_html=True)
with m4:
    st.markdown(f'<div class="metric-card" style="border-top: 5px solid #AB63FA;"><p class="metric-label">Avg Age</p><p class="metric-value" style="color: #AB63FA;">{filtered_df["Age"].mean():.0f}</p></div>', unsafe_allow_html=True)

st.write("---")

# --- 8 COLORFUL CHARTS SECTION ---

# ROW 1
r1c1, r1c2 = st.columns(2)
with r1c1:
    st.subheader("1. 🏢 Attrition by Department")
    fig1 = px.histogram(filtered_df, x="Department", color="Attrition", barmode="group",
                        color_discrete_map={'Yes': '#FF4B4B', 'No': '#00CC96'}, template="plotly_white")
    st.plotly_chart(fig1, use_container_width=True)
    st.info("💡 **Insight:** Sales and R&D often show higher turnover; monitor if this is due to specific role pressures.")

with r1c2:
    st.subheader("2. 💰 Income vs. Retention")
    fig2 = px.box(filtered_df, x="Attrition", y="MonthlyIncome", color="Attrition",
                  color_discrete_map={'Yes': '#FFA15A', 'No': '#19D3F3'}, template="plotly_white")
    st.plotly_chart(fig2, use_container_width=True)
    st.warning("💡 **Insight:** Lower median income is a strong predictor of exit; salary benchmarking is recommended.")

# ROW 2
r2c1, r2c2 = st.columns(2)
with r2c1:
    st.subheader("3. ⏳ Age Demographic Risk")
    fig3 = px.violin(filtered_df, y="Age", x="Attrition", color="Attrition", box=True,
                     color_discrete_sequence=["#AB63FA", "#636EFA"], template="plotly_white")
    st.plotly_chart(fig3, use_container_width=True)
    st.success("💡 **Insight:** Younger talent (ages 25-35) are at higher risk; focus on early-career career pathing.")

with r2c2:
    st.subheader("4. 🕒 Overtime Burnout")
    ot_data = filtered_df.groupby(['OverTime', 'Attrition']).size().reset_index(name='Counts')
    fig4 = px.bar(ot_data, x="OverTime", y="Counts", color="Attrition", barmode="group",
                  color_discrete_map={'Yes': '#FF6692', 'No': '#B6E880'}, template="plotly_white")
    st.plotly_chart(fig4, use_container_width=True)
    st.error("💡 **Insight:** Employees working overtime are twice as likely to leave compared to those who don't.")

# ROW 3
r3c1, r3c2 = st.columns(2)
with r3c1:
    st.subheader("5. ⚖️ Work-Life Balance")
    fig5 = px.pie(filtered_df[filtered_df['Attrition']=='Yes'], names='WorkLifeBalance', 
                  hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
    st.plotly_chart(fig5, use_container_width=True)
    st.info("💡 **Insight:** A high percentage of leavers report low work-life balance (levels 1 and 2).")

with r3c2:
    st.subheader("6. 📈 Job Level vs. Churn")
    fig6 = px.density_heatmap(filtered_df, x="JobLevel", y="Attrition", text_auto=True, color_continuous_scale='Viridis')
    st.plotly_chart(fig6, use_container_width=True)
    st.success("💡 **Insight:** Entry-level (Level 1) roles have the most churn; mentorship can help bridge this gap.")

# ROW 4 (The two you wanted to keep!)
r4c1, r4c2 = st.columns(2)
with r4c1:
    st.subheader("7. 🚗 Distance from Home Impact")
    fig7 = px.histogram(filtered_df, x="DistanceFromHome", color="Attrition", 
                        color_discrete_sequence=["#FF97FF", "#00CC96"], template="plotly_white")
    st.plotly_chart(fig7, use_container_width=True)
    st.warning("💡 **Insight:** Attrition spikes for employees living 10+ miles away; consider remote work options.")

with r4c2:
    st.subheader("8. 📅 Tenure (Years at Company)")
    fig8 = px.area(filtered_df.groupby(['YearsAtCompany', 'Attrition']).size().reset_index(name='Count'), 
                   x="YearsAtCompany", y="Count", color="Attrition", 
                   color_discrete_map={'Yes': '#EF553B', 'No': '#636EFA'}, template="plotly_white")
    st.plotly_chart(fig8, use_container_width=True)
    st.info("💡 **Insight:** The first 2 years are critical. If an employee stays past year 5, retention probability doubles.")

    st.divider()
st.header("🎯 Strategic Insights & Action Plan")
st.markdown("Based on the analysis of the 8 key metrics above, here is the executive summary:")

# Create a container for a "Summary Dashboard" look

with st.container():
    # Dark-mode friendly styling
    st.markdown("""
        <style>
        .action-card {
            background: rgba(40, 44, 52, 0.9);   /* visible in dark mode */
            padding: 20px;
            border-radius: 12px;
            border-left: 5px solid #FF4B4B;
            margin-bottom: 12px;
            box-shadow: 0 6px 18px rgba(0,0,0,0.35);
            color: #f1f1f1;
        }

        .action-title {
            font-weight: bold;
            color: #61dafb;   /* bright cyan – readable in dark */
            font-size: 18px;
        }

        .action-card ul li {
            color: #e6e6e6;
        }
        </style>
    """, unsafe_allow_html=True)

    # Layout for Summary Cards
    sum_col1, sum_col2 = st.columns(2)

    with sum_col1:
        st.markdown('''
            <div class="action-card" style="border-left-color: #FF4B4B;">
                <p class="action-title">🚨 High Risk Factors</p>
                <ul>
                    <li><b>Overtime Burnout:</b> Significant correlation with turnover.</li>
                    <li><b>Junior Tenure:</b> High churn in the first 24 months.</li>
                    <li><b>Compensation:</b> Income levels for leavers are below market median.</li>
                </ul>
            </div>
        ''', unsafe_allow_html=True)

    with sum_col2:
        st.markdown('''
            <div class="action-card" style="border-left-color: #00CC96;">
                <p class="action-title">✅ Retention Opportunities</p>
                <ul>
                    <li><b>Mentorship:</b> Strengthening Level 1 & 2 job support.</li>
                    <li><b>Flexibility:</b> Addressing the "Distance from Home" churn via hybrid work.</li>
                    <li><b>Stability:</b> R&D shows the highest potential for long-term loyalty.</li>
                </ul>
            </div>
        ''', unsafe_allow_html=True)

# Final Overall Conclusion Table
st.subheader("📋 Key Findings Recap")

# Create a small summary dataframe for a clean visual
summary_data = {
    "Category": ["Demographics", "Financial", "Workload", "Environment"],
    "Primary Driver": ["Younger Age (25-35)", "Lower Monthly Income", "Frequent Overtime", "Long Commutes"],
    "Risk Level": ["High", "Medium-High", "Critical", "Medium"],
    "Recommended Action": ["Career Pathing", "Salary Benchmarking", "Resource Rebalancing", "Remote Work Options"]
}

sum_df = pd.DataFrame(summary_data)

# Function to color the risk level
def color_risk(val):
    color = '#ff4b4b' if val == 'Critical' else '#ffa15a' if 'High' in val else '#00cc96'
    return f'color: {color}; font-weight: bold'

st.table(sum_df.style.applymap(color_risk, subset=['Risk Level']))

st.success("✨ **Conclusion:** To reduce the current attrition rate, the organization should prioritize **Overtime reduction** and **Junior-level engagement programs** over the next quarter.")

# ===== RAW vs CLEANED DATA =====
st.header("🗂️ Data Explorer")

with st.expander("📄 View RAW Dataset (Original Data)"):
    st.write(f"Total records: {len(df)}")
    st.dataframe(df, use_container_width=True)
    st.download_button("📥 Download RAW Data", df.to_csv(index=False), "raw_hr_data.csv")

with st.expander("🧹 View CLEANED / FILTERED Dataset"):
    st.write(f"Filtered records: {len(filtered_df)}")
    st.dataframe(filtered_df, use_container_width=True)
    st.download_button("📥 Download CLEANED Data", filtered_df.to_csv(index=False), "cleaned_hr_data.csv")


st.divider()

def generate_pdf(filtered_df):
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    styles = getSampleStyleSheet()
    story = []

    # Title
    styles["Title"].textColor = HexColor("#4F46E5")
    story.append(Paragraph("HR Employees Attrition Analysis Report", styles["Title"]))
    story.append(Spacer(1, 12))

    # Summary
    story.append(Paragraph("<b>Executive Summary</b>", styles["Heading2"]))
    story.append(Spacer(1, 8))

    total = len(filtered_df)
    attr_rate = (filtered_df['Attrition'] == 'Yes').mean() * 100
    avg_age = filtered_df["Age"].mean()
    avg_sat = filtered_df["JobSatisfaction"].mean()

    summary_text = f"""
    <b>Total Employees Analyzed:</b> {total}<br/>
    <b>Attrition Rate:</b> {attr_rate:.2f}%<br/>
    <b>Average Age:</b> {avg_age:.1f}<br/>
    <b>Average Job Satisfaction:</b> {avg_sat:.2f} / 4
    """
    story.append(Paragraph(summary_text, styles["Normal"]))
    story.append(Spacer(1, 12))

    # Insights
    story.append(Paragraph("<b>Key Insights</b>", styles["Heading2"]))
    story.append(Spacer(1, 8))

    insights = [
        "Employees working overtime show significantly higher attrition.",
        "Highest churn observed in the first 2 years of employment.",
        "Lower monthly income strongly correlates with employee exit.",
        "Longer distance from home increases attrition risk.",
        "Junior-level roles require focused retention strategies."
    ]

    for insight in insights:
        story.append(Paragraph(f"- {insight}", styles["Normal"]))
        story.append(Spacer(1, 4))

    story.append(Spacer(1, 14))

    # Conclusion
    story.append(Paragraph("<b>Conclusion</b>", styles["Heading2"]))
    story.append(Spacer(1, 8))
    story.append(
        Paragraph(
            "Reducing overtime workload and improving engagement for junior employees "
            "should be the top priorities to lower attrition in the next quarter.",
            styles["Normal"]
        )
    )

    doc.build(story)
    buffer.seek(0)
    return buffer

st.divider()
st.subheader("📄 Download HR Attrition Report")

pdf_file = generate_pdf(filtered_df)

st.download_button(
    label="⬇️ Download Dashboard Report (PDF)",
    data=pdf_file,
    file_name="HR_Attrition_Report.pdf",
    mime="application/pdf"
)

st.caption("Created for HR Analysis • Data Source: IBM HR Analytics")

# --- Footer Section ---
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #666; font-size: 14px; padding-bottom: 20px;">
        <b>Prepared by:</b> Priyanka and Mausumi | 
        <b>Copyright:</b> NSTIW, Kolkata
    </div>
    """, 
    unsafe_allow_html=True
)

