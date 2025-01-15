<template>
  <div class="monthly-stats-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>月收入统计</span>
          <el-date-picker
            v-model="selectedMonth"
            type="month"
            placeholder="选择月份"
            @change="handleMonthChange">
          </el-date-picker>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :span="24">
          <div ref="monthlyTrendChartRef" style="height: 400px"></div>
        </el-col>
      </el-row>

      <el-row :gutter="20" class="stats-cards">
        <el-col :span="8" v-for="stat in monthlyStats" :key="stat.label">
          <el-card :class="['stat-card', stat.type]">
            <template #header>
              <div class="stat-header">
                {{ stat.label }}
              </div>
            </template>
            <div class="stat-value">
              ¥{{ stat.value.toLocaleString() }}
            </div>
            <div class="stat-compare" :class="stat.trend">
              <el-icon>
                <component :is="stat.trend === 'up' ? 'ArrowUp' : 'ArrowDown'" />
              </el-icon>
              {{ Math.abs(stat.percentage).toFixed(1) }}% 相比上月
            </div>
          </el-card>
        </el-col>
      </el-row>

      <el-divider />

      <el-row :gutter="20">
        <el-col :span="12">
          <div ref="typeDistributionChartRef" style="height: 400px"></div>
        </el-col>
        <el-col :span="12">
          <el-table
            :data="monthlyTypeStats"
            style="width: 100%">
            <el-table-column
              prop="type"
              label="收入类型">
              <template #default="{ row }">
                <el-tag :type="getTagType(row.type)">
                  {{ row.label }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column
              prop="amount"
              label="金额">
              <template #default="{ row }">
                ¥{{ row.amount.toLocaleString() }}
              </template>
            </el-table-column>
            <el-table-column
              prop="percentage"
              label="占比">
              <template #default="{ row }">
                {{ row.percentage.toFixed(1) }}%
              </template>
            </el-table-column>
          </el-table>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useIncomeStore } from '../store/income'
import * as echarts from 'echarts'
import dayjs from 'dayjs'
import { ArrowUp, ArrowDown } from '@element-plus/icons-vue'

const store = useIncomeStore()
const selectedMonth = ref(new Date())
const monthlyTrendChartRef = ref(null)
const typeDistributionChartRef = ref(null)
let trendChart = null
let distributionChart = null

const incomeTypes = [
  { value: 'salary', label: '工资收入' },
  { value: 'thesis', label: '论文代写' },
  { value: 'subsidy', label: '补贴收入' },
  { value: 'other', label: '其他收入' }
]

const getTagType = (type) => {
  const types = {
    salary: 'success',
    thesis: 'warning',
    subsidy: 'info',
    other: ''
  }
  return types[type] || ''
}

const monthlyIncomes = computed(() => {
  if (!selectedMonth.value) return []
  
  const monthStart = dayjs(selectedMonth.value).startOf('month')
  const monthEnd = dayjs(selectedMonth.value).endOf('month')
  
  return store.incomes.filter(income => {
    const incomeDate = dayjs(income.date)
    return incomeDate.isAfter(monthStart) && incomeDate.isBefore(monthEnd)
  })
})

const lastMonthIncomes = computed(() => {
  if (!selectedMonth.value) return []
  
  const lastMonthStart = dayjs(selectedMonth.value).subtract(1, 'month').startOf('month')
  const lastMonthEnd = dayjs(selectedMonth.value).subtract(1, 'month').endOf('month')
  
  return store.incomes.filter(income => {
    const incomeDate = dayjs(income.date)
    return incomeDate.isAfter(lastMonthStart) && incomeDate.isBefore(lastMonthEnd)
  })
})

const monthlyTotal = computed(() => {
  return monthlyIncomes.value.reduce((sum, income) => sum + income.amount, 0)
})

const lastMonthTotal = computed(() => {
  return lastMonthIncomes.value.reduce((sum, income) => sum + income.amount, 0)
})

const monthlyStats = computed(() => {
  const totalChange = lastMonthTotal.value ? 
    ((monthlyTotal.value - lastMonthTotal.value) / lastMonthTotal.value) * 100 : 0

  const avgDaily = monthlyTotal.value / dayjs(selectedMonth.value).daysInMonth()
  const lastAvgDaily = lastMonthTotal.value / dayjs(selectedMonth.value).subtract(1, 'month').daysInMonth()
  const avgChange = lastAvgDaily ? 
    ((avgDaily - lastAvgDaily) / lastAvgDaily) * 100 : 0

  return [
    {
      label: '月总收入',
      value: monthlyTotal.value,
      type: 'total',
      trend: totalChange >= 0 ? 'up' : 'down',
      percentage: totalChange
    },
    {
      label: '日均收入',
      value: avgDaily,
      type: 'average',
      trend: avgChange >= 0 ? 'up' : 'down',
      percentage: avgChange
    },
    {
      label: '上月对比',
      value: lastMonthTotal.value,
      type: 'compare',
      trend: totalChange >= 0 ? 'up' : 'down',
      percentage: totalChange
    }
  ]
})

const monthlyTypeStats = computed(() => {
  const stats = {}
  incomeTypes.forEach(type => {
    stats[type.value] = 0
  })

  monthlyIncomes.value.forEach(income => {
    stats[income.type] += income.amount
  })

  return Object.entries(stats).map(([type, amount]) => {
    const typeInfo = incomeTypes.find(t => t.value === type)
    return {
      type,
      label: typeInfo.label,
      amount,
      percentage: monthlyTotal.value ? (amount / monthlyTotal.value) * 100 : 0
    }
  })
})

const initTrendChart = () => {
  const days = Array.from(
    { length: dayjs(selectedMonth.value).daysInMonth() },
    (_, i) => i + 1
  )
  
  const dailyData = new Array(days.length).fill(0)
  monthlyIncomes.value.forEach(income => {
    const day = dayjs(income.date).date() - 1
    dailyData[day] += income.amount
  })

  const option = {
    title: {
      text: '日收入趋势',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      formatter: '{b}日: ¥{c}'
    },
    xAxis: {
      type: 'category',
      data: days,
      name: '日期'
    },
    yAxis: {
      type: 'value',
      name: '金额',
      axisLabel: {
        formatter: '¥{value}'
      }
    },
    series: [
      {
        data: dailyData,
        type: 'line',
        smooth: true,
        areaStyle: {
          opacity: 0.3
        },
        lineStyle: {
          width: 3
        },
        symbolSize: 8
      }
    ]
  }

  if (!trendChart) {
    trendChart = echarts.init(monthlyTrendChartRef.value)
  }
  trendChart.setOption(option)
}

const initDistributionChart = () => {
  const option = {
    title: {
      text: '收入类型分布',
      left: 'center'
    },
    tooltip: {
      trigger: 'item',
      formatter: '{b}: ¥{c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: 10,
      top: 'middle'
    },
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: false
        },
        emphasis: {
          label: {
            show: true,
            fontSize: '20',
            fontWeight: 'bold'
          }
        },
        data: monthlyTypeStats.value.map(stat => ({
          name: stat.label,
          value: stat.amount
        }))
      }
    ]
  }

  if (!distributionChart) {
    distributionChart = echarts.init(typeDistributionChartRef.value)
  }
  distributionChart.setOption(option)
}

const handleMonthChange = () => {
  initTrendChart()
  initDistributionChart()
}

onMounted(async () => {
  await store.fetchIncomes()
  initTrendChart()
  initDistributionChart()
  
  window.addEventListener('resize', () => {
    trendChart?.resize()
    distributionChart?.resize()
  })
})
</script>

<style scoped>
.monthly-stats-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stats-cards {
  margin: 30px 0;
}

.stat-card {
  text-align: center;
}

.stat-header {
  font-size: 16px;
  color: #606266;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  margin: 10px 0;
}

.stat-compare {
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 5px;
}

.stat-compare.up {
  color: #67C23A;
}

.stat-compare.down {
  color: #F56C6C;
}

.stat-card.total .stat-value {
  color: #409EFF;
}

.stat-card.average .stat-value {
  color: #67C23A;
}

.stat-card.compare .stat-value {
  color: #E6A23C;
}

.el-divider {
  margin: 30px 0;
}
</style> 