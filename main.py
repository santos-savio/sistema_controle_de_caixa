#!/usr/bin/env python3
"""
Sistema de Controle de Caixa - Entry Point Único

Este é o ponto de entrada centralizado que gerencia toda a inicialização
do sistema, incluindo banco de dados, configurações e inicialização da aplicação.
"""

import sys
import os
import argparse
import logging
from pathlib import Path

# Adicionar diretório raiz ao path
sys.path.insert(0, str(Path(__file__).parent))

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def initialize_system():
    """Inicializa todo o sistema (banco, configurações, dados iniciais)"""
    try:
        logger.info("Iniciando inicialização do sistema...")
        
        # Importar e inicializar banco de dados
        from init_db import init_database
        logger.info("Inicializando banco de dados...")
        init_database()
        
        # Importar e inicializar configurações do sistema
        from init_system_config import init_system_config
        logger.info("Inicializando configurações do sistema...")
        init_system_config()
        
        # Importar e inicializar métodos de pagamento
        from init_payment_methods import init_payment_methods
        logger.info("Inicializando métodos de pagamento...")
        init_payment_methods()
        
        logger.info("✅ Sistema inicializado com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro na inicialização do sistema: {e}")
        return False


def reset_system():
    """Reseta o banco de dados e reinicializa o sistema"""
    try:
        logger.info("Resetando sistema...")
        
        # Importar e executar reset
        from reset_database import reset_database
        reset_database()
        
        # Reinicializar sistema completo
        initialize_system()
        
        logger.info("✅ Sistema resetado e reinicializado com sucesso!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Erro no reset do sistema: {e}")
        return False


def start_application():
    """Inicia a aplicação Flask"""
    try:
        logger.info("Iniciando aplicação...")
        
        # Importar launcher
        from launcher import main as launcher_main
        launcher_main()
        
    except Exception as e:
        logger.error(f"❌ Erro ao iniciar aplicação: {e}")
        sys.exit(1)


def main():
    """Função principal - entry point do sistema"""
    parser = argparse.ArgumentParser(
        description='Sistema de Controle de Caixa',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  python main.py                    # Inicia aplicação com verificação
  python main.py --init-only       # Apenas inicializa sistema
  python main.py --reset           # Reseta e reinicializa
  python main.py --no-init         # Inicia sem inicialização
        """
    )
    
    parser.add_argument(
        '--init-only',
        action='store_true',
        help='Apenas inicializa o sistema (banco, configs, dados)'
    )
    
    parser.add_argument(
        '--reset',
        action='store_true',
        help='Reseta banco de dados e reinicializa sistema'
    )
    
    parser.add_argument(
        '--no-init',
        action='store_true',
        help='Inicia aplicação sem verificar inicialização'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Modo verbose com logging detalhado'
    )
    
    args = parser.parse_args()
    
    # Configurar nível de log
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Executar ação solicitada
    try:
        if args.init_only:
            # Apenas inicialização
            success = initialize_system()
            sys.exit(0 if success else 1)
            
        elif args.reset:
            # Reset e reinicialização
            success = reset_system()
            sys.exit(0 if success else 1)
            
        else:
            # Iniciar aplicação (com ou sem inicialização)
            if not args.no_init:
                # Verificar se sistema está inicializado
                try:
                    from app import create_app
                    app = create_app()
                    
                    # Tentar conectar ao banco para verificar
                    with app.app_context():
                        from app.models import db
                        db.engine.execute('SELECT 1')
                        logger.info("✅ Sistema já inicializado")
                        
                except Exception:
                    logger.info("🔍 Sistema não inicializado, executando inicialização...")
                    success = initialize_system()
                    if not success:
                        logger.error("❌ Falha na inicialização, abortando")
                        sys.exit(1)
            
            # Iniciar aplicação
            start_application()
            
    except KeyboardInterrupt:
        logger.info("👋 Aplicação encerrada pelo usuário")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Erro fatal: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
