-- ============================================
-- SISTEMA DE GESTÃO DE ALUNOS - SCHEMA SQL
-- ============================================
-- Este script deve ser executado no SQL Editor do Supabase
-- para criar todas as tabelas necessárias para o sistema.

-- ============================================
-- 1. TABELA DE UNIDADES
-- ============================================
CREATE TABLE IF NOT EXISTS unidades (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100) NOT NULL UNIQUE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Inserir unidades padrão
INSERT INTO unidades (nome) VALUES 
    ('Ipiaú'),
    ('Irecê')
ON CONFLICT (nome) DO NOTHING;

-- ============================================
-- 2. TABELA DE INSTRUTORES
-- ============================================
CREATE TABLE IF NOT EXISTS instrutores (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    unidade_id INTEGER NOT NULL REFERENCES unidades(id) ON DELETE CASCADE,
    ativo BOOLEAN DEFAULT TRUE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índice para busca rápida por unidade
CREATE INDEX IF NOT EXISTS idx_instrutores_unidade ON instrutores(unidade_id);
CREATE INDEX IF NOT EXISTS idx_instrutores_ativo ON instrutores(ativo);

-- ============================================
-- 3. TABELA DE ALUNOS
-- ============================================
CREATE TABLE IF NOT EXISTS alunos (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    data_inicio DATE NOT NULL,
    curso_matriculado VARCHAR(200) NOT NULL,
    tipo_plano VARCHAR(50) NOT NULL CHECK (tipo_plano IN ('Convencional', 'Acelerado', 'Flex')),
    modulo VARCHAR(100),
    aulas INTEGER CHECK (aulas >= 1 AND aulas <= 30),
    dia_horario JSONB, -- Estrutura: {"segunda": "20:00", "quarta": "18:00"}
    situacao_academica VARCHAR(50) NOT NULL CHECK (situacao_academica IN ('Regular', 'Atrasado', 'Adiantado', 'Formado(a)')),
    observacoes TEXT,
    pagamento_parcelas VARCHAR(50), -- Pode ser número (1-30) ou "Concluído"
    instrutor_id INTEGER REFERENCES instrutores(id) ON DELETE SET NULL,
    unidade_id INTEGER NOT NULL REFERENCES unidades(id) ON DELETE CASCADE,
    arquivado BOOLEAN DEFAULT FALSE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para otimização de consultas
CREATE INDEX IF NOT EXISTS idx_alunos_unidade ON alunos(unidade_id);
CREATE INDEX IF NOT EXISTS idx_alunos_instrutor ON alunos(instrutor_id);
CREATE INDEX IF NOT EXISTS idx_alunos_arquivado ON alunos(arquivado);
CREATE INDEX IF NOT EXISTS idx_alunos_situacao ON alunos(situacao_academica);

-- ============================================
-- 4. TABELA DE AÇÕES
-- ============================================
CREATE TABLE IF NOT EXISTS acoes (
    id SERIAL PRIMARY KEY,
    aluno_id INTEGER NOT NULL REFERENCES alunos(id) ON DELETE CASCADE,
    acao_proposta TEXT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'Pendente' CHECK (status IN ('Pendente', 'Concluída')),
    instrutor_resp_id INTEGER REFERENCES instrutores(id) ON DELETE SET NULL,
    data_proposta DATE NOT NULL DEFAULT CURRENT_DATE,
    data_conclusao DATE,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Índices para busca rápida
CREATE INDEX IF NOT EXISTS idx_acoes_aluno ON acoes(aluno_id);
CREATE INDEX IF NOT EXISTS idx_acoes_status ON acoes(status);
CREATE INDEX IF NOT EXISTS idx_acoes_instrutor ON acoes(instrutor_resp_id);

-- ============================================
-- 5. TABELA DE LOGS
-- ============================================
CREATE TABLE IF NOT EXISTS logs (
    id SERIAL PRIMARY KEY,
    instrutor_id INTEGER REFERENCES instrutores(id) ON DELETE SET NULL,
    atividade TEXT NOT NULL,
    data_hora TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    unidade_id INTEGER REFERENCES unidades(id) ON DELETE CASCADE
);

-- Índice para busca por data e unidade
CREATE INDEX IF NOT EXISTS idx_logs_data ON logs(data_hora DESC);
CREATE INDEX IF NOT EXISTS idx_logs_unidade ON logs(unidade_id);
CREATE INDEX IF NOT EXISTS idx_logs_instrutor ON logs(instrutor_id);

-- ============================================
-- 6. TRIGGERS PARA ATUALIZAR TIMESTAMP
-- ============================================

-- Função para atualizar o campo atualizado_em
CREATE OR REPLACE FUNCTION atualizar_timestamp()
RETURNS TRIGGER AS $$
BEGIN
    NEW.atualizado_em = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para instrutores
CREATE TRIGGER trigger_atualizar_instrutores
    BEFORE UPDATE ON instrutores
    FOR EACH ROW
    EXECUTE FUNCTION atualizar_timestamp();

-- Trigger para alunos
CREATE TRIGGER trigger_atualizar_alunos
    BEFORE UPDATE ON alunos
    FOR EACH ROW
    EXECUTE FUNCTION atualizar_timestamp();

-- Trigger para ações
CREATE TRIGGER trigger_atualizar_acoes
    BEFORE UPDATE ON acoes
    FOR EACH ROW
    EXECUTE FUNCTION atualizar_timestamp();

-- ============================================
-- 7. VIEWS ÚTEIS (OPCIONAL)
-- ============================================

-- View para alunos ativos com informações completas
CREATE OR REPLACE VIEW view_alunos_ativos AS
SELECT 
    a.id,
    a.nome,
    a.data_inicio,
    a.curso_matriculado,
    a.tipo_plano,
    a.modulo,
    a.aulas,
    a.dia_horario,
    a.situacao_academica,
    a.observacoes,
    a.pagamento_parcelas,
    i.nome AS instrutor_nome,
    u.nome AS unidade_nome,
    a.criado_em,
    a.atualizado_em,
    (SELECT COUNT(*) FROM acoes WHERE aluno_id = a.id AND status = 'Pendente') AS acoes_pendentes
FROM alunos a
LEFT JOIN instrutores i ON a.instrutor_id = i.id
LEFT JOIN unidades u ON a.unidade_id = u.id
WHERE a.arquivado = FALSE
ORDER BY a.nome;

-- View para logs com informações completas
CREATE OR REPLACE VIEW view_logs_completos AS
SELECT 
    l.id,
    i.nome AS instrutor_nome,
    l.atividade,
    l.data_hora,
    u.nome AS unidade_nome
FROM logs l
LEFT JOIN instrutores i ON l.instrutor_id = i.id
LEFT JOIN unidades u ON l.unidade_id = u.id
ORDER BY l.data_hora DESC;

-- ============================================
-- 8. POLÍTICAS DE SEGURANÇA (RLS - OPCIONAL)
-- ============================================
-- Se você quiser usar Row Level Security no Supabase,
-- descomente as linhas abaixo:

-- ALTER TABLE unidades ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE instrutores ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE alunos ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE acoes ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE logs ENABLE ROW LEVEL SECURITY;

-- Exemplo de política (permitir tudo para usuários autenticados):
-- CREATE POLICY "Permitir tudo para autenticados" ON alunos
--     FOR ALL USING (auth.role() = 'authenticated');

-- ============================================
-- FIM DO SCRIPT
-- ============================================

-- Para verificar se tudo foi criado corretamente, execute:
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
