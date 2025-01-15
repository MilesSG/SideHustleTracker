import { defineStore } from 'pinia'
import api from '../api/config'

export const useIncomeStore = defineStore('income', {
  state: () => ({
    incomes: [],
    goals: [],
    goalsProgress: [],
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
    },

    currentGoal: (state) => {
      if (!state.goals.length || !state.goalsProgress.length) return null
      
      const latestGoal = state.goalsProgress.reduce((latest, current) => {
        if (!latest) return current
        const latestDate = new Date(latest.goal.end_date)
        const currentDate = new Date(current.goal.end_date)
        return currentDate > latestDate ? current : latest
      }, null)
      
      return latestGoal
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
    },

    // 目标相关的 actions
    async fetchGoals() {
      this.loading = true
      try {
        const [goals, progress] = await Promise.all([
          api.get('/api/goals'),
          api.get('/api/goals/progress')
        ])
        this.goals = goals
        this.goalsProgress = progress
        this.error = null
      } catch (error) {
        console.error('Failed to fetch goals:', error)
        this.error = error.message || '获取目标失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    async addGoal(goal) {
      this.loading = true
      try {
        const data = await api.post('/api/goals', goal)
        this.goals.push(data)
        await this.fetchGoals() // 重新获取进度
        this.error = null
        return data
      } catch (error) {
        console.error('Failed to add goal:', error)
        this.error = error.message || '添加目标失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    async updateGoal(id, goal) {
      this.loading = true
      try {
        const data = await api.put(`/api/goals/${id}`, goal)
        const index = this.goals.findIndex(g => g.id === id)
        if (index !== -1) {
          this.goals[index] = data
        }
        await this.fetchGoals() // 重新获取进度
        this.error = null
        return data
      } catch (error) {
        console.error('Failed to update goal:', error)
        this.error = error.message || '更新目标失败'
        throw error
      } finally {
        this.loading = false
      }
    },

    async deleteGoal(id) {
      this.loading = true
      try {
        await api.delete(`/api/goals/${id}`)
        this.goals = this.goals.filter(goal => goal.id !== id)
        await this.fetchGoals() // 重新获取进度
        this.error = null
      } catch (error) {
        console.error('Failed to delete goal:', error)
        this.error = error.message || '删除目标失败'
        throw error
      } finally {
        this.loading = false
      }
    }
  }
}) 