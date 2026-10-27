// Binance vadeli emir defteri derinliği — Frankfurt'ta dakikada bir ölçüm (💧 likidite dipte için). Araştırma: ld_kontrol.py, ld_anlik.py (dal arastirma3).
import { defineConfig } from '@neon/config/v1';
export default defineConfig({
  functions: {
    derinlik: { name: 'Binance vadeli derinlik', source: './index.ts' },
  },
  triggers: {
    dakika: { type: 'schedule', function: 'derinlik', cron: '*/3 * * * *', functionPath: '/ornek' },
  },
  buckets: {
    derinlik: {},
  },
});
