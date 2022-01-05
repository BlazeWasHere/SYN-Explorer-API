SELECT
    lost_txs.*
FROM
    lost_txs
    INNER JOIN txs ON txs.pending = true
    AND txs.kappa = lost_txs.kappa;