/**
 * CurrencyContext — shared context untuk konversi mata uang
 * Dipisahkan agar tidak ada circular dependency antara JobDetailPage dan VisualizationsTab
 */
import { createContext, useContext, useState } from 'react'

export type Currency = 'USD' | 'IDR' | 'EUR' | 'GBP' | 'JPY' | 'SGD'

export const CURRENCIES = [
  { code: 'USD' as Currency, symbol: '$',   label: 'US Dollar',         rate: 1 },
  { code: 'IDR' as Currency, symbol: 'Rp',  label: 'Indonesian Rupiah', rate: 15800 },
  { code: 'EUR' as Currency, symbol: '€',   label: 'Euro',              rate: 0.92 },
  { code: 'GBP' as Currency, symbol: '£',   label: 'British Pound',     rate: 0.79 },
  { code: 'JPY' as Currency, symbol: '¥',   label: 'Japanese Yen',      rate: 149 },
  { code: 'SGD' as Currency, symbol: 'S$',  label: 'Singapore Dollar',  rate: 1.34 },
]

export const CurrencyContext = createContext<{
  currency: Currency
  setCurrency: (c: Currency) => void
  symbol: string
  rate: number
  format: (v: number) => string
}>({
  currency: 'USD',
  setCurrency: () => {},
  symbol: '$',
  rate: 1,
  format: v => `$${v.toLocaleString()}`,
})

export function useCurrency() {
  return useContext(CurrencyContext)
}

export function CurrencyProvider({ children }: { children: React.ReactNode }) {
  const [currency, setCurrency] = useState<Currency>(
    () => (localStorage.getItem('df_currency') as Currency) || 'USD'
  )
  const meta = CURRENCIES.find(c => c.code === currency) || CURRENCIES[0]

  const format = (v: number): string => {
    const converted = v * meta.rate
    const abs = Math.abs(converted)
    const prefix = converted < 0 ? '-' : ''
    if (currency === 'IDR') {
      if (abs >= 1e9)  return `${prefix}${meta.symbol}${(abs / 1e9).toFixed(1)}M`
      if (abs >= 1e6)  return `${prefix}${meta.symbol}${(abs / 1e6).toFixed(1)}Jt`
      if (abs >= 1e3)  return `${prefix}${meta.symbol}${(abs / 1e3).toFixed(0)}Rb`
      return `${prefix}${meta.symbol}${abs.toFixed(0)}`
    }
    if (abs >= 1e9)  return `${prefix}${meta.symbol}${(abs / 1e9).toFixed(2)}B`
    if (abs >= 1e6)  return `${prefix}${meta.symbol}${(abs / 1e6).toFixed(2)}M`
    if (abs >= 1e3)  return `${prefix}${meta.symbol}${(abs / 1e3).toFixed(1)}K`
    return `${prefix}${meta.symbol}${abs.toFixed(2)}`
  }

  const handleSet = (c: Currency) => {
    localStorage.setItem('df_currency', c)
    setCurrency(c)
  }

  return (
    <CurrencyContext.Provider value={{ currency, setCurrency: handleSet, symbol: meta.symbol, rate: meta.rate, format }}>
      {children}
    </CurrencyContext.Provider>
  )
}
