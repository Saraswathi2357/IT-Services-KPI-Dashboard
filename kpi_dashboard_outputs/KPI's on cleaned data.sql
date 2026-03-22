USE it_services_kpi;

SELECT COUNT(*) FROM clean_projects;
SELECT COUNT(*) FROM clean_employees;
SELECT COUNT(*) FROM clean_clients;
SELECT COUNT(*) FROM clean_timesheets;
SELECT COUNT(*) FROM clean_feedback;

/* KPI 1 — Project Delivery Status */
SELECT
    project_id,
    start_date,
    planned_end_date,
    actual_end_date,
    status,
    CASE
        WHEN actual_end_date <= planned_end_date THEN 'On Time'
        ELSE 'Delayed'
    END AS delivery_status
FROM clean_projects;

/* KPI 2 — Resource Utilisation */
SELECT
    emp_id,
    SUM(billable_hours) /
    (SUM(billable_hours) + SUM(non_billable_hours)) * 100 AS utilisation_rate
FROM clean_timesheets
GROUP BY emp_id;

/* KPI 3 — Avg Satisfaction per Project */
SELECT
    project_id,
    AVG(satisfaction_score) AS avg_score
FROM clean_feedback
GROUP BY project_id;

/* KPI 4 — Client Satisfaction */
SELECT
    cp.client_id,
    AVG(cf.satisfaction_score) AS avg_client_score
FROM clean_feedback cf
JOIN clean_projects cp
    ON cf.project_id = cp.project_id
GROUP BY cp.client_id;

/* KPI 5 — On-Time Delivery % */
SELECT 
    COUNT(CASE 
        WHEN actual_end_date <= planned_end_date THEN 1 
    END) * 100.0 / COUNT(*) AS on_time_delivery_percentage
FROM clean_projects;

/* KPI 6 — Project Status Count */
SELECT 
    status,
    COUNT(*) AS total_projects
FROM clean_projects
GROUP BY status;

/* KPI 7 — Employee Utilisation % */
SELECT 
    emp_id,
    SUM(billable_hours) /
    (SUM(billable_hours) + SUM(non_billable_hours)) * 100 AS utilisation_percentage
FROM clean_timesheets
GROUP BY emp_id;

/* KPI 8 — Revenue per Project */
SELECT 
    project_id,
    budget AS revenue
FROM clean_projects;

/* KPI 9 — Overall Client Satisfaction */
SELECT 
    AVG(satisfaction_score) AS avg_client_satisfaction
FROM clean_feedback;

/* KPI 10 — Revenue by Client */
SELECT 
    cc.client_name,
    SUM(cp.budget) AS total_revenue
FROM clean_projects cp
JOIN clean_clients cc
    ON cp.client_id = cc.client_id
GROUP BY cc.client_name
ORDER BY total_revenue DESC;

/* KPI 11 — Department Workload */
SELECT 
    ce.department,
    SUM(ct.billable_hours) AS total_billable_hours
FROM clean_employees ce
JOIN clean_timesheets ct
    ON ce.emp_id = ct.emp_id
GROUP BY ce.department;