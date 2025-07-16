-- Player Data
CREATE TABLE players (
    id VARCHAR(36) PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_login TIMESTAMPTZ,
    level INT DEFAULT 1,
    xp BIGINT DEFAULT 0,
    credits BIGINT DEFAULT 100,
    health INT DEFAULT 100,
    damage INT DEFAULT 15,
    armor INT DEFAULT 10,
    speed INT DEFAULT 5,
    skill_points INT DEFAULT 0,
    wins INT DEFAULT 0,
    losses INT DEFAULT 0,
    draws INT DEFAULT 0,
    pve_wins INT DEFAULT 0,
    pve_losses INT DEFAULT 0
);

-- Equipment
CREATE TABLE equipment (
    id VARCHAR(36) PRIMARY KEY,
    player_id VARCHAR(36) REFERENCES players(id) ON DELETE CASCADE,
    item_type VARCHAR(20) NOT NULL,
    item_name VARCHAR(50) NOT NULL,
    equipped BOOLEAN DEFAULT false,
    stats JSONB,
    acquired_at TIMESTAMPTZ DEFAULT NOW()
);

-- Battle History
CREATE TABLE battles (
    id VARCHAR(36) PRIMARY KEY,
    player1_id VARCHAR(36) REFERENCES players(id),
    player2_id VARCHAR(36),
    is_ai BOOLEAN DEFAULT false,
    start_time TIMESTAMPTZ DEFAULT NOW(),
    end_time TIMESTAMPTZ,
    winner_id VARCHAR(36),
    events JSONB,
    type VARCHAR(10) CHECK (type IN ('pvp', 'pve', 'tournament'))
);

-- Tournaments
CREATE TABLE tournaments (
    id VARCHAR(36) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    sponsor VARCHAR(50),
    entry_fee BIGINT NOT NULL,
    prize_pool BIGINT DEFAULT 0,
    start_time TIMESTAMPTZ,
    end_time TIMESTAMPTZ,
    status VARCHAR(20) CHECK (status IN ('scheduled', 'running', 'completed')),
    winner_id VARCHAR(36) REFERENCES players(id)
);

-- Transactions
CREATE TABLE transactions (
    id VARCHAR(36) PRIMARY KEY,
    player_id VARCHAR(36) REFERENCES players(id),
    type VARCHAR(20) CHECK (type IN ('purchase', 'payout', 'reward')),
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'USD',
    status VARCHAR(20) CHECK (status IN ('pending', 'completed', 'failed')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB
);

-- Battle Pass
CREATE TABLE battle_passes (
    player_id VARCHAR(36) PRIMARY KEY REFERENCES players(id),
    active BOOLEAN DEFAULT false,
    start_date TIMESTAMPTZ,
    end_date TIMESTAMPTZ,
    level INT DEFAULT 1,
    xp INT DEFAULT 0
);

-- Indexes for performance
CREATE INDEX idx_battles_player ON battles(player1_id);
CREATE INDEX idx_equipment_player ON equipment(player_id);
CREATE INDEX idx_transactions_player ON transactions(player_id);
CREATE INDEX idx_tournaments_time ON tournaments(start_time);
