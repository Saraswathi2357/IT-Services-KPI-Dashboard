import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Output folder inside your current project directory
output_dir = r"C:\Users\Mahadev Saraswathi\Documents\DA Projects\Project1 - IT Services KPI Dashboard\kpi_dashboard_outputs"
os.makedirs(output_dir, exist_ok=True)

# MySQL Connection
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Saras@123",
    database="it_services_kpi"
)
# Load tables into pandas dataframes
projects = pd.read_sql("SELECT * FROM projects", connection)
employees = pd.read_sql("SELECT * FROM employees", connection)
timesheets = pd.read_sql("SELECT * FROM timesheets", connection)
clients = pd.read_sql("SELECT * FROM clients", connection)
feedback = pd.read_sql("SELECT * FROM client_feedback", connection)

# Display first 5 rows
print("Projects Data")
print(projects.head())
print("\nEmployees Data")
print(employees.head())
print("\nClients Data")
print(clients.head())
print("\nTimesheets Data")
print(timesheets.head())
print("\nClient Feedback Data")
print(feedback.head())

#Data Inspection
print("\nProjects Dataset Info")
print(projects.info())
print("\nEmployees Dataset Info")
print(employees.info())
print("\nTimesheets Dataset Info")
print(timesheets.info())
print("\nClients Dataset Info")
print(clients.info())
print("\nClient Feedback Dataset Info")
print(feedback.info())

#Missing Data Detection
print("\nMissing Values in Projects")
print(projects.isnull().sum())
print("\nMissing Values in Employees")
print(employees.isnull().sum())
print("\nMissing Values in Timesheets")
print(timesheets.isnull().sum())
print("\nMissing Values in Clients")
print(clients.isnull().sum())
print("\nMissing Values in Client Feedback")
print(feedback.isnull().sum())

# --------------------------
# 4️ -  Data Cleaning
# --------------------------
for df in [projects, employees, timesheets, clients, feedback]:
    df.drop_duplicates(inplace=True)
    df.reset_index(drop=True, inplace=True)

# Projects
projects['project_name'].fillna('Unknown Project', inplace=True)
projects.dropna(subset=['planned_end_date','actual_end_date'], inplace=True)
projects['budget'] = pd.to_numeric(projects['budget'], errors='coerce')

# Employees
employees['emp_name'].fillna('Unknown', inplace=True)
employees['role'].fillna('Not Specified', inplace=True)
employees['department'].fillna('Not Specified', inplace=True)

# Timesheets
timesheets['billable_hours'] = pd.to_numeric(timesheets['billable_hours'], errors='coerce')
timesheets['non_billable_hours'] = pd.to_numeric(timesheets['non_billable_hours'], errors='coerce')
timesheets.dropna(subset=['emp_id','project_id'], inplace=True)

# Clients
clients['client_name'].fillna('Unknown Client', inplace=True)
clients['industry'].fillna('Not Specified', inplace=True)
clients['location'].fillna('Not Specified', inplace=True)

# Feedback
feedback['satisfaction_score'] = pd.to_numeric(feedback['satisfaction_score'], errors='coerce')
feedback.dropna(subset=['project_id'], inplace=True)

print(" Data Cleaning Completed")

# --------------------------
# 5 -  Feature Engineering
# --------------------------
projects['planned_end_date'] = pd.to_datetime(projects['planned_end_date'])
projects['actual_end_date'] = pd.to_datetime(projects['actual_end_date'])
projects['start_date'] = pd.to_datetime(projects['start_date'])

projects['delivery_delay_days'] = (projects['actual_end_date'] - projects['planned_end_date']).dt.days
projects['on_time'] = projects['delivery_delay_days'] <= 0

# Total hours per project
project_hours = timesheets.groupby('project_id')[['billable_hours','non_billable_hours']].sum().reset_index()
projects = projects.merge(project_hours, on='project_id', how='left')

# Fill missing billable hours with 0
projects['billable_hours'] = projects['billable_hours'].fillna(0)
projects['non_billable_hours'] = projects['non_billable_hours'].fillna(0)

# Average client feedback per project
avg_feedback = feedback.groupby('project_id')['satisfaction_score'].mean().reset_index()
projects = projects.merge(avg_feedback, on='project_id', how='left')

# Merge client info
projects = projects.merge(clients, on='client_id', how='left')
'''
# --------------------------
# 6 -  Push cleaned data to MySQL
# --------------------------
from sqlalchemy import create_engine

engine = create_engine("mysql+mysqlconnector://root:Saras%40123@localhost/it_services_kpi")

projects.to_sql('clean_projects', con=engine, if_exists='replace', index=False)
employees.to_sql('clean_employees', con=engine, if_exists='replace', index=False)
clients.to_sql('clean_clients', con=engine, if_exists='replace', index=False)
timesheets.to_sql('clean_timesheets', con=engine, if_exists='replace', index=False)
feedback.to_sql('clean_feedback', con=engine, if_exists='replace', index=False)

print("Cleaned data pushed to MySQL")

# --------------------------
# 7 - Save cleaned datasets
# --------------------------
projects.to_csv(os.path.join(output_dir, 'clean_projects.csv'), index=False)
employees.to_csv(os.path.join(output_dir, 'clean_employees.csv'), index=False)
clients.to_csv(os.path.join(output_dir, 'clean_clients.csv'), index=False)
timesheets.to_csv(os.path.join(output_dir, 'clean_timesheets.csv'), index=False)
feedback.to_csv(os.path.join(output_dir, 'clean_feedback.csv'), index=False)

print("Cleaned data exported successfully")
'''
# --------------------------
# 8 - Exploratory Data Analysis
# --------------------------
print("\n--- Projects Stats ---")
print(projects.describe(include='all'))

print("\n--- Employees Stats ---")
print(employees.describe(include='all'))

print("\n--- Clients Stats ---")
print(clients.describe(include='all'))

print("\n--- Timesheets Stats ---")
print(timesheets.describe(include='all'))

print("\n--- Feedback Stats ---")
print(feedback.describe(include='all'))

# Save summary tables for documentation
projects.describe(include='all').to_csv(os.path.join(output_dir, 'projects_summary.csv'))
employees.describe(include='all').to_csv(os.path.join(output_dir, 'employees_summary.csv'))
clients.describe(include='all').to_csv(os.path.join(output_dir, 'clients_summary.csv'))
timesheets.describe(include='all').to_csv(os.path.join(output_dir, 'timesheets_summary.csv'))
feedback.describe(include='all').to_csv(os.path.join(output_dir, 'feedback_summary.csv'))

# --------------------------
# 9 -  Visualization – Delivery Trends
# --------------------------
sns.set(style="whitegrid")

# 1. Distribution of delivery delays
plt.figure(figsize=(10,5))
sns.histplot(projects['delivery_delay_days'], bins=20, kde=True, color='skyblue')
plt.title('Distribution of Project Delivery Delays (Days)')
plt.xlabel('Delivery Delay (Days)')
plt.ylabel('Number of Projects')
plt.savefig(os.path.join(output_dir,'delivery_delay_distribution.png'))
plt.show()

# 2. On-time vs Delayed Projects Pie Chart
on_time_count = projects['on_time'].sum()
delayed_count = len(projects) - on_time_count
plt.figure(figsize=(6,6))
plt.pie([on_time_count, delayed_count], labels=['On Time','Delayed'], autopct='%1.1f%%', colors=['green','red'])
plt.title('Project On-Time Delivery Rate')
plt.savefig(os.path.join(output_dir,'on_time_pie.png'))
plt.show()

# 3. Average delay over time
plt.figure(figsize=(12,5))
projects.groupby('planned_end_date')['delivery_delay_days'].mean().plot(marker='o')
plt.title('Average Delivery Delay Over Time')
plt.xlabel('Planned End Date')
plt.ylabel('Average Delay (Days)')
plt.grid(True)
plt.savefig(os.path.join(output_dir,'avg_delay_over_time.png'))
plt.show()

# 4. Budget vs Delivery Delay Scatter
plt.figure(figsize=(10,5))
sns.scatterplot(data=projects, x='budget', y='delivery_delay_days', hue='on_time', palette={True:'green', False:'red'})
plt.title('Project Budget vs Delivery Delay')
plt.xlabel('Budget')
plt.ylabel('Delivery Delay (Days)')
plt.savefig(os.path.join(output_dir,'budget_vs_delay.png'))
plt.show()

# 5. Top clients by average satisfaction score
top_clients = projects.groupby('client_name')['satisfaction_score'].mean().sort_values(ascending=False)
plt.figure(figsize=(10,5))
top_clients.plot(kind='bar', color='purple')
plt.title('Top Clients by Average Satisfaction')
plt.ylabel('Satisfaction Score')
plt.xticks(rotation=45)
plt.savefig(os.path.join(output_dir,'top_clients_satisfaction.png'))
plt.show()

# 6. Top projects by billable hours
plt.figure(figsize=(10,5))
sns.barplot(data=projects.sort_values('billable_hours', ascending=False), x='project_name', y='billable_hours', palette='Blues_d')
plt.xticks(rotation=45)
plt.title('Top Projects by Billable Hours')
plt.ylabel('Billable Hours')
plt.xlabel('Project Name')
plt.savefig(os.path.join(output_dir,'top_projects_hours.png'))
plt.show()

# --------------------------
# 10 - Summary Findings
# --------------------------
total_projects = len(projects)
avg_delay = projects['delivery_delay_days'].mean()
avg_budget = projects['budget'].mean()

print("\n====== Summary Findings ======")
print(f"Total Projects: {total_projects}")
print(f"Projects Delivered On Time: {on_time_count} ({on_time_count/total_projects*100:.2f}%)")
print(f"Projects Delayed: {delayed_count} ({delayed_count/total_projects*100:.2f}%)")
print(f"Average Delivery Delay: {avg_delay:.2f} days")
print(f"Average Project Budget: ${avg_budget:.2f}")

# Top 5 delayed projects
top_delayed = projects.sort_values('delivery_delay_days', ascending=False).head(5)
print("\nTop 5 Delayed Projects:")
print(top_delayed[['project_id','project_name','delivery_delay_days','client_name','budget','status']])

# Top 5 projects by satisfaction
top_satisfaction = projects.sort_values('satisfaction_score', ascending=False).head(5)
print("\nTop 5 Projects by Client Satisfaction:")
print(top_satisfaction[['project_id','project_name','client_name','satisfaction_score']])

