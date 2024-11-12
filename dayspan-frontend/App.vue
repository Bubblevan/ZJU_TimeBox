<template>
  <v-app id="dayspan" v-cloak>
    <!-- 顶部横幅图片 -->
    <v-container fluid class="banner-container">
      <v-img
        src="../dayspan-frontend/src/assets/banner.png"
        height="100"
        contain
        class="banner-image"
      ></v-img>
    </v-container>

    <!-- 顶部导航栏 -->
    <v-app-bar app color="primary" dark>
      <!-- Logo -->
      <v-toolbar-title>
        <img
          src="https://pixe1ran9e.oss-cn-hangzhou.aliyuncs.com/phto.png"
          alt="Logo"
          class="mr-2"
          height="30"
        />
        ZJU-LLM-Calendar
      </v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn text>首页</v-btn>
      <v-btn text>关于我们</v-btn>
      <v-btn text>联系我们</v-btn>
      <v-btn text @click="login">登录</v-btn>
    </v-app-bar>

    <div class="calendar-container">
      <!-- 现有的日历组件 -->
      <ds-calendar-app
        ref="app"
        :calendar="calendar"
        :read-only="readOnly"
        @change="saveState"
        :types="[{ type: 'week', size: 1, label: 'Week' }]"
      >
        <!-- 省略现有的 slot 内容 -->
        <template slot="title"> ZJU-LLM-Calendar </template>

        <template slot="eventPopover" slot-scope="slotData">
          <ds-calendar-event-popover
            v-bind="slotData"
            :read-only="readOnly"
            @finish="saveState"
          >
          </ds-calendar-event-popover>
        </template>

        <template
          slot="eventCreatePopover"
          slot-scope="{ placeholder, calendar }"
        >
          <ds-calendar-event-create-popover
            :calendar-event="placeholder"
            :calendar="calendar"
            :close="$refs.app.$refs.calendar.clearPlaceholder"
            @create-edit="$refs.app.editPlaceholder"
            @create-popover-closed="saveState"
          ></ds-calendar-event-create-popover>
        </template>

        <template slot="eventTimeTitle" slot-scope="{ details }">
          <div>
            <v-icon
              class="ds-ev-icon"
              v-if="details.icon"
              size="14"
              :style="{ color: details.forecolor }"
            >
              {{ details.icon }}
            </v-icon>
            <strong class="ds-ev-title" style="word-wrap: break-word">{{ details.title }}</strong>
          </div>
        </template>
      </ds-calendar-app>

      <div class="empty-space">
        <!-- 省略现有的菜单和标签内容 -->
        <el-menu default-active="2">
          <el-menu-item index="1">
            <img
              src="https://pixe1ran9e.oss-cn-hangzhou.aliyuncs.com/phto.png"
              alt="ZJU"
              style="width: 40px; height: 40px"
            />
            <span slot="title" style="margin-left: 5px">用户设置</span>
          </el-menu-item>
          <el-menu-item index="2">
            <i class="el-icon-document"></i>
            <span slot="title">日历</span>
          </el-menu-item>
          <el-menu-item index="3">
            <i class="el-icon-menu"></i>
            <span slot="title">RAG</span>
          </el-menu-item>
        </el-menu>
        <div class="tags">
          <div class="title-container">
            <span class="tags-title" style="margin-top: 10px">添加或删除分类</span>
          </div>
          <el-tag
            :key="tag"
            v-for="tag in dynamicTags"
            closable
            :disable-transitions="false"
            @close="handleClose(tag)"
            style="margin-top: 5px; margin-left: 5px"
          >
            {{ tag }}
          </el-tag>
          <el-input
            class="input-new-tag"
            v-if="inputVisible"
            v-model="inputValue"
            ref="saveTagInput"
            size="small"
            style="margin-top: 5px; margin-left: 5px"
            @keyup.enter.native="handleInputConfirm"
            @blur="handleInputConfirm"
          >
          </el-input>
          <el-button
            v-else
            class="button-new-tag"
            size="small"
            style="margin-top: 5px; margin-left: 5px; margin-bottom: 5px"
            @click="showInput"
            >添加分类</el-button
          >
        </div>
      </div>
    </div>

    <!-- 底部横幅 -->
    <v-footer app color="primary" dark>
      <v-container>
        <v-row>
          <v-col cols="12" md="6">
            © 2024 浙江大学 | All Rights Reserved
          </v-col>
          <v-col cols="12" md="6" class="text-right">
            <v-btn text small>隐私政策</v-btn>
            <v-btn text small>服务条款</v-btn>
            <v-btn icon small>
              <v-icon>mdi-facebook</v-icon>
            </v-btn>
            <v-btn icon small>
              <v-icon>mdi-twitter</v-icon>
            </v-btn>
          </v-col>
        </v-row>
      </v-container>
    </v-footer>
  </v-app>
</template>

<script>
import { Calendar, Month } from "dayspan";
import Vue from "vue";
import axios from "axios";

export default {
  name: "app",

  data: () => ({
    storeKey: "dayspanState",
    calendar: Calendar.weeks(),
    readOnly: true,
    defaultEvents: [],
    dynamicTags: ["公示通知", "社会实践", "科研"],
    inputVisible: false,
    inputValue: "",
  }),

  mounted() {
    window.app = this.$refs.app;

    this.loadState();
    this.fetchNotices(); // 加载通知数据
  },

  methods: {
    getCalendarTime(calendarEvent) {
      let sa = calendarEvent.start.format("a");
      let ea = calendarEvent.end.format("a");
      let sh = calendarEvent.start.format("h");
      let eh = calendarEvent.end.format("h");

      if (calendarEvent.start.minute !== 0) {
        sh += calendarEvent.start.format(":mm");
      }

      if (calendarEvent.end.minute !== 0) {
        eh += calendarEvent.end.format(":mm");
      }

      return sa === ea ? sh + " - " + eh + ea : sh + sa + " - " + eh + ea;
    },

    saveState() {
      let state = this.calendar.toInput(true);
      let json = JSON.stringify(state);

      localStorage.setItem(this.storeKey, json);
    },

    loadState() {
      let state = {};

      try {
        let savedState = JSON.parse(localStorage.getItem(this.storeKey));
        if (savedState) {
          state = savedState;
          state.preferToday = false;
        }
      } catch (e) {
        // eslint-disable-next-line
        console.log(e);
      }

      state.events = this.defaultEvents;

      state.events.forEach((ev) => {
        let defaults = this.$dayspan.getDefaultEventDetails();

        ev.data = Vue.util.extend(defaults, ev.data);
      });

      this.$refs.app.setState(state);
    },

    handleClose(tag) {
      this.dynamicTags.splice(this.dynamicTags.indexOf(tag), 1);
    },

    showInput() {
      this.inputVisible = true;
      this.$nextTick(() => {
        this.$refs.saveTagInput.$refs.input.focus();
      });
    },

    handleInputConfirm() {
      let inputValue = this.inputValue;
      if (inputValue) {
        this.dynamicTags.push(inputValue);
      }
      this.inputVisible = false;
      this.inputValue = "";
    },

    // 获取通知数据
    async fetchNotices() {
      try {
        const response = await axios.get("http://127.0.0.1:8000/notices/");
        this.defaultEvents = response.data.map((notice) => {
          // 解析日期以获取月份和日期
          const dateObj = new Date(notice.date);
          const month = dateObj.getMonth() + 1; // getMonth() 返回0-11
          const dayOfMonth = dateObj.getDate();

          return {
            data: {
              title: notice.title,
              color: "#2196F3", // 默认颜色
              description: notice.content,
              link: notice.link, // 如果需要在日历中使用链接
            },
            schedule: {
              month: [Month[month]],
              dayOfMonth: [dayOfMonth],
              times: [0],
              duration: 60,
              durationUnit: "minutes",
            },
          };
        });
        this.loadState();
      } catch (error) {
        // console.error("Error fetching notices:", error);
      }
    },

    // 登录方法示例
    login() {
      // 这里添加登录逻辑
      alert("登录功能尚未实现！");
    },
  },
};
</script>

<style>
body,
html,
#app,
#dayspan {
  font-family: Roboto, sans-serif !important;
  width: 100%;
  height: 100%;
  overflow-y: auto;
  margin: 0;
  padding: 0;
}

.v-application {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.banner-container {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.banner-image {
  width: 100%; /* 使图片宽度填满容器 */
  max-height: 100px; /* 根据需要调整高度 */
  object-fit: cover; /* 确保图片覆盖容器 */
}

.calendar-container {
  flex: 1;
  display: flex;
  justify-content: space-between;
  padding: 20px; /* 添加一些内边距 */
}

.empty-space {
  width: 10%;
  display: flex;
  flex-direction: column;
}

.title-container {
  display: flex;
  justify-content: center;
  margin-top: 15px;
}

.tags {
  margin-right: 10px;
  margin-top: 20px;
  width: 100%;
  border-radius: 3px;
  background: #fafafa;
  box-shadow: -6px -6px 7px #dedede, 6px 6px 7px #e2e2e2;
  padding: 10px;
}

.el-tag + .el-tag {
  margin-left: 10px;
}

.button-new-tag {
  margin-left: 10px;
  height: 32px;
  line-height: 30px;
  padding-top: 0;
  padding-bottom: 0;
}

.input-new-tag {
  width: 90px;
  margin-left: 10px;
  vertical-align: bottom;
}

.v-btn--flat,
.v-text-field--solo .v-input__slot {
  background-color: #f5f5f5 !important;
  margin-bottom: 8px !important;
}

.ds-calendar-event-popover-card .v-card__text .v-list .v-list__tile__title,
.ds-calendar-event-popover-card .v-card__text .v-list .v-list__tile__sub-title {
  white-space: normal;
  word-wrap: break-word;
}
</style>
