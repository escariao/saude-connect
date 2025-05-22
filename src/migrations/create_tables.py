"""
Script para criar as tabelas categories e activities caso não existam
"""
from flask import Flask
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.models.user import db
from sqlalchemy import text, inspect

app = Flask(__name__)

# Configuração do banco de dados
database_url = os.getenv('DATABASE_URL')

if database_url:
    # Configuração para Render (PostgreSQL)
    database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Configuração para desenvolvimento local (MySQL)
    app.config['SQLALCHEMY_DATABASE_URI'] = f"mysql+pymysql://{os.getenv('DB_USERNAME', 'root')}:{os.getenv('DB_PASSWORD', 'password')}@{os.getenv('DB_HOST', 'localhost')}:{os.getenv('DB_PORT', '3306')}/{os.getenv('DB_NAME', 'mydb')}"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Lista de categorias profissionais em ordem alfabética
CATEGORIES = [
    "Acupunturista",
    "Auxiliar de Saúde Bucal",
    "Cuidador",
    "Dentista",
    "Doula",
    "Educador Físico",
    "Enfermeiro",
    "Farmacêutico Clínico",
    "Fisioterapeuta",
    "Fonoaudiólogo",
    "Maqueiro",
    "Massoterapeuta",
    "Nutricionista",
    "Podólogo",
    "Psicólogo",
    "Técnico de Enfermagem",
    "Técnico em Análises Clínicas",
    "Técnico em Radiologia",
    "Terapeuta Ocupacional"
]

def run_migration():
    with app.app_context():
        try:
            inspector = inspect(db.engine)
            
            # Verificar se a tabela categories existe
            if not inspector.has_table('categories'):
                print("A tabela 'categories' não existe. Criando tabela...")
                
                # Criar a tabela categories
                if database_url:  # PostgreSQL (Render)
                    db.session.execute(text("""
                    CREATE TABLE categories (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        description TEXT
                    )
                    """))
                else:  # MySQL (local)
                    db.session.execute(text("""
                    CREATE TABLE categories (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(100) NOT NULL,
                        description TEXT
                    )
                    """))
                
                db.session.commit()
                print("Tabela 'categories' criada com sucesso!")
                
                # Inserir as categorias
                for category in CATEGORIES:
                    db.session.execute(
                        text("INSERT INTO categories (name) VALUES (:name)"),
                        {"name": category}
                    )
                
                db.session.commit()
                print(f"Inseridas {len(CATEGORIES)} categorias com sucesso!")
            else:
                print("A tabela 'categories' já existe.")
            
            # Verificar se a tabela activities existe
            if not inspector.has_table('activities'):
                print("A tabela 'activities' não existe. Criando tabela...")
                
                # Criar a tabela activities
                if database_url:  # PostgreSQL (Render)
                    db.session.execute(text("""
                    CREATE TABLE activities (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100) NOT NULL UNIQUE,
                        description TEXT,
                        category_id INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        CONSTRAINT fk_activities_category FOREIGN KEY (category_id) REFERENCES categories(id)
                    )
                    """))
                else:  # MySQL (local)
                    db.session.execute(text("""
                    CREATE TABLE activities (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(100) NOT NULL UNIQUE,
                        description TEXT,
                        category_id INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        CONSTRAINT fk_activities_category FOREIGN KEY (category_id) REFERENCES categories(id)
                    )
                    """))
                
                db.session.commit()
                print("Tabela 'activities' criada com sucesso!")
            else:
                print("A tabela 'activities' já existe.")
                
                # Verificar se a coluna category_id existe
                columns = [c['name'] for c in inspector.get_columns('activities')]
                if 'category_id' not in columns:
                    print("Adicionando coluna category_id à tabela activities...")
                    
                    # Adicionar a coluna category_id
                    db.session.execute(text("ALTER TABLE activities ADD COLUMN category_id INTEGER"))
                    
                    # Adicionar a chave estrangeira
                    db.session.execute(text("ALTER TABLE activities ADD CONSTRAINT fk_activities_category FOREIGN KEY (category_id) REFERENCES categories(id)"))
                    
                    db.session.commit()
                    print("Coluna category_id adicionada com sucesso!")
                else:
                    print("A coluna category_id já existe na tabela activities.")
                    
            print("Migração concluída com sucesso!")
                    
        except Exception as e:
            db.session.rollback()
            print(f"Erro durante a migração: {e}")

if __name__ == '__main__':
    run_migration()
