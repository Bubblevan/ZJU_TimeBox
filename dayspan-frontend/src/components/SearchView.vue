<template>
    <div class="search-view">
      <el-input
        v-model="searchQuery"
        placeholder="请输入搜索内容"
        @input="onSearch"
        style="margin-bottom: 20px;"
      >
        <template slot="append">
          <el-button icon="el-icon-search" @click="onSearch"></el-button>
        </template>
      </el-input>
      <el-table
        :data="searchResults"
        style="width: 100%"
      >
        <el-table-column
          prop="title"
          label="标题"
          width="180"
        >
        </el-table-column>
        <el-table-column
          prop="date"
          label="日期"
          width="180"
        >
        </el-table-column>
        <el-table-column
          prop="content"
          label="内容"
        >
        </el-table-column>
        <el-table-column
          fixed="right"
          label="操作"
          width="120"
        >
          <template slot-scope="scope">
            <el-button
              type="text"
              size="small"
              @click="viewDetail(scope.row)"
            >查看</el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  
  export default {
    name: 'SearchView',
    data() {
      return {
        searchQuery: '',
        searchResults: [],
        tableNames: ["kyjs", "bksy", "ckc", "danqing", "jiaoliu", "lantian", "qsxy", "yunfeng"],
      };
    },
    methods: {
      async onSearch() {
        if (this.searchQuery.trim() === '') {
          this.searchResults = [];
          return;
        }
  
        try {
          const allNotices = [];
          for (const tableName of this.tableNames) {
            const response = await axios.get(`http://127.0.0.1:8000/notices/${tableName}`);
            allNotices.push(...response.data);
          }
  
          this.searchResults = allNotices.filter(notice =>
            notice.title.includes(this.searchQuery) ||
            notice.content.includes(this.searchQuery)
          );
        } catch (error) {
          console.error("Error fetching notices:", error);
        }
      },
      viewDetail(row) {
        this.$alert(row.content, row.title, {
          confirmButtonText: '确定',
        });
      }
    }
  };
  </script>
  
  <style scoped>
  .search-view {
    padding: 20px;
  }
  
  .el-table .el-button {
    margin: 0;
  }
  </style>
  