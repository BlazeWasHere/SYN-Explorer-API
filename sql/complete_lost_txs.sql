-- It is faster to use ./cli/complete_lost_txs.py
UPDATE
    txs
SET
    to_tx_hash = _lost_txs.to_tx_hash,
    received_token = _lost_txs.received_token,
    received_value = _lost_txs.received_value,
    received_time = _lost_txs.received_time,
    swap_success = _lost_txs.swap_success,
    pending = false
FROM
    (
        SELECT
            lost_txs.to_tx_hash,
            lost_txs.received_token,
            lost_txs.received_value,
            lost_txs.received_time,
            lost_txs.swap_success
        FROM
            lost_txs
            INNER JOIN txs ON txs.kappa = lost_txs.kappa
    ) AS _lost_txs
WHERE
    txs.pending = true
    AND txs.kappa in (
        SELECT
            kappa
        FROM
            lost_txs
    );