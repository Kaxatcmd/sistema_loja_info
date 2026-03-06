# PONTOS DE INTERESSE - SISTEMA DE GESTÃO DE LOJA DE INFORMÁTICA

## Tema e Objetivo

Sistema desktop para gestão integrada de loja de informática, permitindo clientes explorar catálogo seguramente e administrador gerir inventário em tempo real.

## Implementação

Python 3.8+ com interface Tkinter, base de dados MariaDB, autenticação via bcrypt (12 rounds), prepared statements para segurança.

## Atores e Funcionalidades

Cliente: autenticação, busca/filtro de produtos, carrinho, compra. Administrador: gerir produtos, consultar vendas, visualizar clientes.

## Modelo de Dados

Quatro tabelas normalizadas: clientes, produtos, vendas, itens_venda. Relacionamentos de integridade referencial, índices de performance.

## Interface

Janela principal com abas (ttk.Notebook), diálogos modais, validações em tempo real, feedback visual de status.

## Conclusão

Aplicação funcional, segura e escalável, conforme especificação de fluxograma, pronta para produção com manutenção clara.
