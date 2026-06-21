-- Script khởi tạo database cho SQL Server
-- Chạy script này trên SQL Server Management Studio (SSMS) hoặc sqlcmd

-- Tạo database nếu chưa tồn tại
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'medipredict')
BEGIN
    CREATE DATABASE medipredict;
END
GO

USE medipredict;
GO

-- Tạo bảng diseases
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='diseases' AND xtype='U')
BEGIN
    CREATE TABLE diseases (
        id INT IDENTITY(1,1) PRIMARY KEY,
        name NVARCHAR(200) NOT NULL,
        group_name NVARCHAR(100) NOT NULL,
        risk_level VARCHAR(20) NOT NULL,
        icon NVARCHAR(10) NULL,
        description NVARCHAR(1000) NOT NULL,
        symptoms NVARCHAR(2000) NULL,
        causes NVARCHAR(2000) NULL,
        diagnosis NVARCHAR(2000) NULL,
        treatment NVARCHAR(2000) NULL,
        created_at DATETIME DEFAULT GETDATE(),
        updated_at DATETIME DEFAULT GETDATE()
    );
    CREATE INDEX ix_diseases_id ON diseases(id);
END
GO

-- Tạo bảng drugs
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='drugs' AND xtype='U')
BEGIN
    CREATE TABLE drugs (
        id INT IDENTITY(1,1) PRIMARY KEY,
        code VARCHAR(20) NOT NULL,
        name NVARCHAR(200) NOT NULL,
        group_name NVARCHAR(100) NOT NULL,
        manufacturer NVARCHAR(200) NOT NULL,
        status VARCHAR(20) NOT NULL,
        rating FLOAT NULL,
        price NVARCHAR(50) NULL,
        component NVARCHAR(500) NULL,
        usage_info NVARCHAR(1000) NULL,
        dosage NVARCHAR(500) NULL,
        side_effects NVARCHAR(1000) NULL,
        contraindications NVARCHAR(1000) NULL,
        created_at DATETIME DEFAULT GETDATE(),
        updated_at DATETIME DEFAULT GETDATE()
    );
    CREATE INDEX ix_drugs_id ON drugs(id);
END
GO

-- Tạo bảng disease_drug_mappings
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='disease_drug_mappings' AND xtype='U')
BEGIN
    CREATE TABLE disease_drug_mappings (
        id INT IDENTITY(1,1) PRIMARY KEY,
        disease_id INT NOT NULL,
        drug_id INT NOT NULL,
        priority INT NOT NULL,
        match_score INT NULL,
        created_at DATETIME DEFAULT GETDATE(),
        updated_at DATETIME DEFAULT GETDATE()
    );
    CREATE INDEX ix_disease_drug_mappings_id ON disease_drug_mappings(id);
END
GO

-- Tạo bảng prediction_histories
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='prediction_histories' AND xtype='U')
BEGIN
    CREATE TABLE prediction_histories (
        id INT IDENTITY(1,1) PRIMARY KEY,
        user_id VARCHAR(255) NOT NULL,
        symptoms_input NVARCHAR(2000) NOT NULL,
        predicted_disease_id INT NOT NULL,
        accuracy_score INT NOT NULL,
        status VARCHAR(20) NULL,
        created_at DATETIME DEFAULT GETDATE(),
        updated_at DATETIME DEFAULT GETDATE()
    );
    CREATE INDEX ix_prediction_histories_id ON prediction_histories(id);
END
GO

-- Tạo bảng users
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='users' AND xtype='U')
BEGIN
    CREATE TABLE users (
        id VARCHAR(255) PRIMARY KEY,
        email VARCHAR(255) NOT NULL,
        name NVARCHAR(255) NULL,
        role VARCHAR(50) NOT NULL DEFAULT 'user',
        created_at DATETIME DEFAULT GETDATE(),
        last_login DATETIME NULL
    );
    CREATE INDEX ix_users_id ON users(id);
END
GO

-- Tạo bảng oidc_states
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='oidc_states' AND xtype='U')
BEGIN
    CREATE TABLE oidc_states (
        id INT IDENTITY(1,1) PRIMARY KEY,
        state VARCHAR(255) NOT NULL UNIQUE,
        nonce VARCHAR(255) NOT NULL,
        code_verifier VARCHAR(255) NOT NULL,
        expires_at DATETIME NOT NULL,
        created_at DATETIME DEFAULT GETDATE()
    );
    CREATE INDEX ix_oidc_states_id ON oidc_states(id);
    CREATE INDEX ix_oidc_states_state ON oidc_states(state);
END
GO

PRINT N'Tất cả bảng đã được tạo thành công!';
GO