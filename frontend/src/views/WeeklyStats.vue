<template>
  <div class="weekly-stats-container">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>周收入统计</span>
          <el-date-picker
            v-model="selectedWeek"
            type="week"
            format="YYYY 第 ww 周"
            placeholder="选择周"
            @change="handleWeekChange">
          </el-date-picker>
        </div>
      </template>

      <el-row :gutter="20">
        <el-col :span="12">
          <div ref="weeklyBarChartRef" style="height: 400px"></div>
        </el-col>
        <el-col :span="12">
          <div ref="weeklyPieChartRef" style="height: 400px"></div>
        </el-col>
      </el-row>

      <el-divider />

      <el-table
        :data="weeklyIncomes"
        style="width: 100%"
        :default-sort="{ prop: 'date', order: 'ascending' }">
        <el-table-column
          prop="date"
          label="日期"
          sortable
          width="180">
          <template #default="{ row }">
            {{ new Date(row.date).toLocaleDateString() }}
          </template>
        </el-table-column>
        <el-table-column
          prop="type"
          label="类型"
          width="180">
          <template #default="{ row }">
            <el-tag :type="getTagType(row.type)">
              {{ getTypeLabel(row.type) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column
          prop="amount"
          label="金额"
          sortable>
          <template #default="{ row }">
            ¥{{ row.amount.toLocaleString() }}
          </template>
        </el-table-column>
        <el-table-column
          prop="description"
          label="描述">
        </el-table-column>
      </el-table>

      <div class="weekly-summary">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="本周总收入">
            <span class="total-amount">¥{{ weeklyTotal.toLocaleString() }}</span>
          </el-descriptions-item>
          <el-descriptions-item label="日均收入">
            <span class="daily-average">¥{{ dailyAverage.toLocaleString() }}</span>
          </el-descriptions-item>
        </el-descriptions>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useIncomeStore } from '../store/income'
import * as echarts from 'echarts'
import dayjs from 'dayjs'
import weekOfYear from 'dayjs/plugin/weekOfYear'

dayjs.extend(weekOfYear)

const store = useIncomeStore()
const selectedWeek = ref(new Date())
const weeklyBarChartRef = ref(null)
const weeklyPieChartRef = ref(null)
let barChart = null
let pieChart = null

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

const getTypeLabel = (type) => {
  const found = incomeTypes.find(t => t.value === type)
  return found ? found.label : type
}

const weeklyIncomes = computed(() => {
  if (!selectedWeek.value) return []
  
  const weekStart = dayjs(selectedWeek.value).startOf('week')
  const weekEnd = dayjs(selectedWeek.value).endOf('week')
  
  return store.incomes.filter(income => {
    const incomeDate = dayjs(income.date)
    return incomeDate.isAfter(weekStart) && incomeDate.isBefore(weekEnd)
  })
})

const weeklyTotal = computed(() => {
  return weeklyIncomes.value.reduce((sum, income) => sum + income.amount, 0)
})

const dailyAverage = computed(() => {
  return weeklyTotal.value / 7
})

const initBarChart = () => {
  const dailyData = new Array(7).fill(0)
  const days = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
  
  weeklyIncomes.value.forEach(income => {
    const day = new Date(income.date).getDay()
    dailyData[day] += income.amount
  })

  const option = {
    title: {
      text: '日收入分布',
      left: 'center'
    },
    tooltip: {
      trigger: 'axis',
      formatter: '{b}: ¥{c}'
    },
    xAxis: {
      type: 'category',
      data: days
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: '¥{value}'
      }
    },
    series: [
      {
        data: dailyData,
        type: 'bar',
        showBackground: true,
        backgroundStyle: {
          color: 'rgba(180, 180, 180, 0.2)'
        },
        itemStyle: {
          color: '#409EFF'
        }
      }
    ]
  }

  if (!barChart) {
    barChart = echarts.init(weeklyBarChartRef.value)
  }
  barChart.setOption(option)
}

const initPieChart = () => {
  const typeData = {}
  incomeTypes.forEach(type => {
    typeData[type.value] = 0
  })

  weeklyIncomes.value.forEach(income => {
    typeData[income.type] += income.amount
  })

  const pieData = Object.entries(typeData).map(([type, amount]) => ({
    name: getTypeLabel(type),
    value: amount
  }))

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
        data: pieData
      }
    ]
  }

  if (!pieChart) {
    pieChart = echarts.init(weeklyPieChartRef.value)
  }
  pieChart.setOption(option)
}

const handleWeekChange = () => {
  initBarChart()
  initPieChart()
}

watch(weeklyIncomes, () => {
  initBarChart()
  initPieChart()
})

onMounted(async () => {
  await store.fetchIncomes()
  initBarChart()
  initPieChart()
  
  window.addEventListener('resize', () => {
    barChart?.resize()
    pieChart?.resize()
  })
})
</script>

<style scoped>
.weekly-stats-container {
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.weekly-summary {
  margin-top: 20px;
}

.total-amount {
  color: #67C23A;
  font-size: 20px;
  font-weight: bold;
}

.daily-average {
  color: #409EFF;
  font-size: 20px;
  font-weight: bold;
}

.el-divider {
  margin: 30px 0;
}
</style> 