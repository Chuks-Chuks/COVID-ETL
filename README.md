This is an enhanced, production-grade ETL pipeline that integrates dbt, Postgres, AWS S3, and advanced DevOps practices covering cloud migrations, modern data stack, CI/CD, and data quality. This project will simulate enterprise-grade workflows while ensuring the granular data of COVID is preserved for downstream users

---

### **Enhanced Project Overview**
**Objective**: Build a scalable ELT pipeline that ingests COVID-19 data, stages it in AWS S3, loads it into Postgres, transforms it with dbt, ensures GDPR-like data quality, and deploys via CI/CD.  
**Tools**:  
- **Orchestration**: Apache Airflow  
- **Cloud**: AWS S3 (raw storage), Postgres (warehouse)  
- **Transformation**: dbt + Postgres  
- **Data Quality**: Great Expectations + dbt tests  
- **DevOps**: Docker, GitHub Actions, Terraform (IaC)  

---

### **Architecture**
```
Extract (API) → Stage (AWS S3) → Load (Snowflake) → Transform (dbt) → Validate (GE/dbt) → Visualize (Power BI)
