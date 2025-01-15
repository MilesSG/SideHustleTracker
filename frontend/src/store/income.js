import { defineStore } from 'pinia'
import api from '../api/config'

export const useIncomeStore = defineStore('income', {
  state: () => ({
    incomes: [],
    loading: false,
    error: null
  }),
  
  getters: {
    totalIncome: (state) => {
      return state.incomes.reduce((sum, income) => sum + income.amount, 0)
    },
    
    incomeByType: (state) => {
      return (type) => state.incomes.filter(income => income.type === type)
    },
    
    weeklyStats: (state) => {
      const stats = {}
      state.incomes.forEach(income => {
        const week = new Date(income.date).toISOString().slice(0, 10)
        if (!stats[week]) stats[week] = 0
        stats[week] += income.amount
      })
      return stats
    },
    
    monthlyStats: (state) => {
      const stats = {}
      state.incomes.forEach(income => {
        const month = new Date(income.date).toISOString().slice(0, 7)
        if (!stats[month]) stats[month] = 0
        stats[month] += income.amount
      })
      return stats
    }
  },
  
  actions: {
    async fetchIncomes() {
      this.loading = true
      try {
        const data = await api.get('/api/incomes')
        this.incomes = data
        this.error = null
      } catch (error) {
        this.error = error.message
        console.error('Failed to fetch incomes:', error)
      } finally {
        this.loading = false
      }
    },
    
    async addIncome(income) {
      this.loading = true
      try {
        const data = await api.post('/api/incomes', income)
        this.incomes.push(data)
        this.error = null
        return data
      } catch (error) {
        this.error = error.message
        console.error('Failed to add income:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async updateIncome(id, income) {
      this.loading = true
      try {
        const data = await api.put(`/api/incomes/${id}`, income)
        const index = this.incomes.findIndex(i => i.id === id)
        if (index !== -1) {
          this.incomes[index] = data
        }
        this.error = null
        return data
      } catch (error) {
        this.error = error.message
        console.error('Failed to update income:', error)
        throw error
      } finally {
        this.loading = false
      }
    },
    
    async deleteIncome(id) {
      this.loading = true
      try {
        await api.delete(`/api/incomes/${id}`)
        this.incomes = this.incomes.filter(income => income.id !== id)
        this.error = null
      } catch (error) {
        this.error = error.message
        console.error('Failed to delete income:', error)
        throw error
      } finally {
        this.loading = false
      }
    }
  }
}) 