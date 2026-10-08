-- Migration da fixture sintética, executada em schema isolado com rollback no QA.
CREATE TABLE clientes (
    clinic_id text NOT NULL,
    id integer NOT NULL,
    nome text NOT NULL,
    email text NOT NULL UNIQUE,
    PRIMARY KEY (clinic_id, id)
);
CREATE TABLE pedidos (
    id integer PRIMARY KEY,
    clinic_id text NOT NULL,
    cliente_id integer NOT NULL,
    status text NOT NULL CHECK (status IN ('pendente', 'pago')),
    criado_em timestamptz NOT NULL,
    CONSTRAINT pedidos_cliente_fk FOREIGN KEY (clinic_id, cliente_id)
        REFERENCES clientes (clinic_id, id)
);
