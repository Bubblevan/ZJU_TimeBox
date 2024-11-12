<template>
  <v-app id="dayspan" v-cloak>
    <div class="calendar-container">
      
      <ds-calendar-app
        ref="app"
        :calendar="calendar"
        :read-only="readOnly"
        @change="saveState"
        :types="[{ type: 'week', size: 1, label: 'Week' }, { type: 'month', size: 1, label: 'Month' }]"
      >
        <template slot="title"> ZJU-LLM-Calendar </template>

        <template slot="eventPopover" slot-scope="slotData">
          <ds-calendar-event-popover
            v-bind="slotData"
            :read-only="readOnly"
            @finish="saveState"
          >
          </ds-calendar-event-popover>
        </template>
        

        <template slot="eventCreatePopover" slot-scope="{ placeholder, calendar }">
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
        <el-menu default-active="2">
          <el-menu-item index="1" @click="fetchAllTablesData">
            <img
              src="../src/assets/logo.png"
              alt="ZJU"
              style="width: 40px; height: 40px"
            />
            <span slot="title" style="margin-left: 5px">日 历</span>
          </el-menu-item>
          <el-menu-item index="2">
            <i class="el-icon-refresh"></i>
            <span slot="title" @click="refreshData">立即刷新</span>
          </el-menu-item>
        </el-menu>

        <div class="tags">
          <div class="title-container">
            <span class="tags-title" style="margin-top: 10px">通知分类</span>
          </div>
          <el-tag
            :key="tag.tableName"
            v-for="tag in dynamicTags"
            closable
            :disable-transitions="false"
            @click="handleTagClick(tag.tableName)"
            @close="handleClose(tag)"
            style="margin-top: 5px; margin-left: 5px"
          >
            {{ tag.name }}
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
          >添加分类</el-button>
        </div>
      </div>
      
    </div>
      <!-- 对话框部分 -->
      <div class="chat-container">
        <div class="chat-window">
          <div v-for="(message, index) in chatMessages" :key="index" class="chat-message">
            <span :class="message.role === 'user' ? 'user-message' : 'bot-message'">
              {{ message.content }}
              <!-- 关闭按钮 -->
              <el-button 
                v-if="message.role === 'bot'" 
                type="text" 
                icon="el-icon-close" 
                @click="closeMessage(index)">
              </el-button>
            </span>
          </div>
        </div>
        <div class="chat-input-container">
          <el-button @click="sendMessage" type="primary">发送</el-button>
          <el-input
            v-model="userInput"
            placeholder="输入您的问题..."
            @keyup.enter="sendMessage"
            clearable
          ></el-input>
          
        </div>
      </div>
    <!-- Banner section -->
    <!-- <div class="bottom-banner">
      <div class="footer-content">
        <span class="footer-link" @click="navigateTo('privacy')">隐私政策</span>
        <span class="footer-link" @click="navigateTo('terms')">使用条款</span>
        <span class="footer-link" @click="navigateTo('help')">帮助中心</span>
        <span class="footer-link" @click="navigateTo('contact')">联系我们</span>
      </div>
      <div class="footer-note">
        &copy; 2024 ZJU-TIMEBOX. 保留所有权利。
      </div>
    </div> -->
  </v-app>
</template>

<script>
import { Calendar, Month } from "dayspan";
import axios from "axios";
import "element-ui/lib/theme-chalk/index.css";
// import MarkdownIt from "markdown-it";

export default {
  name: "app",

  data: () => ({
    storeKey: "dayspanState",
    calendar: Calendar.weeks(),
    readOnly: true,
    defaultEvents: [],
    dynamicTags: [
      { name: "科研竞赛", tableName: "kyjs" },
      { name: "本科生院", tableName: "bksy" },
      { name: "竺院通知", tableName: "ckc" },
      { name: "丹青学园", tableName: "danqing" },
      { name: "对外交流", tableName: "jiaoliu" },
      { name: "蓝田学园", tableName: "lantian" },
      { name: "求是学院", tableName: "qsxy" },
      { name: "云峰学园", tableName: "yunfeng" },
    ],
    inputVisible: false,
    inputValue: "",
    selectedTableName: null,

    // 聊天功能相关数据
    chatMessages: [],  // 用于保存聊天记录
    userInput: "",     // 用户输入的内容
  }),

  mounted() {
    window.app = this.$refs.app;
    this.fetchNotices(); // 默认加载所有通知
  },

  methods: {
    // 使用 markdown-it 解析 Markdown 内容
    // renderMarkdown(content) {
    //   return this.md.render(content);
    // },

    // 发送消息到后端并获取回复
    async sendMessage() {
      if (!this.userInput.trim()) return; // 检查输入是否为空
      const question = this.userInput.trim();

      // 添加用户消息到聊天记录
      this.chatMessages.push({ role: "user", content: question });
      this.userInput = ""; // 清空输入框

      try {
        // 请求后端 API 获取回答
        const response = await axios.post("http://127.0.0.1:8000/ask", { question });
        const answer = response.data.answer;

        // 添加机器人回复到聊天记录
        this.chatMessages.push({ role: "bot", content: answer });
      } catch (error) {
        console.error("Error fetching answer:", error);
        this.chatMessages.push({ role: "bot", content: "抱歉，我无法回答您的问题。" });
      }
    },

    // 关闭消息
    closeMessage(index) {
      this.chatMessages.splice(index, 1);
    },

        // 获取所有表的数据
    async fetchAllTablesData() {
      try {
        const allData = [];
        for (const tag of this.dynamicTags) {
          const response = await axios.get(`http://127.0.0.1:8000/notices/${tag.tableName}`);
          allData.push(...response.data);
        }
        this.tableData = allData;
        this.$message.success("所有表数据已加载");
      } catch (error) {
        console.error("Error fetching table data:", error);
        this.$message.error("加载表数据失败");
      }
    },

    async refreshData() {
      try {
        const response = await axios.post("http://127.0.0.1:8000/run_crawlers");
        this.$message.success(response.data.message); // 成功时弹出提示消息
      } catch (error) {
        console.error("Error starting crawlers:", error);
        this.$message.error("Failed to start crawlers."); // 失败时弹出错误消息
      }
    },

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
        console.log(e);
      }
      state.events = this.defaultEvents;
      state.events.forEach((ev) => {
        let defaults = this.$dayspan.getDefaultEventDetails();
        ev.data = { ...defaults, ...ev.data };
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

    handleTagClick(tableName) {
      this.selectedTableName = tableName;
      this.fetchNoticesByCategory(tableName);
    },

    async fetchNotices() {
      try {
        const allNotices = [];
        for (const tag of this.dynamicTags) {
          const response = await axios.get(`http://127.0.0.1:8000/notices/${tag.tableName}`);
          allNotices.push(...response.data.map(notice => ({ ...notice, tableName: tag.tableName })));
        }

        const monthNames = [
          "JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE",
          "JULY", "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER"
        ];

        const colorMap = {
          kyjs: "#2196F3",
          bksy: "#4CAF50",
          ckc: "#FFC107",
          danqing: "#E91E63",
          jiaoliu: "#9C27B0",
          lantian: "#3F51B5",
          qsxy: "#009688",
          yunfeng: "#FF5722",
        };

        this.defaultEvents = allNotices.map(notice => {
          const dateObj = new Date(notice.date);
          const monthIndex = dateObj.getMonth();
          const monthName = monthNames[monthIndex];
          const monthEnum = Month[monthName];
          const dayOfMonth = dateObj.getDate();
          const hour = dateObj.getHours();

          return {
            data: {
              title: notice.title,
              color: colorMap[notice.tableName],
              description: notice.content,
              link: notice.link,
            },
            schedule: {
              month: [monthEnum],
              dayOfMonth: [dayOfMonth],
              times: [hour],
              duration: 60,
              durationUnit: "minutes",
            },
          };
        });

        this.loadState();
      } catch (error) {
        console.error("Error fetching all notices:", error);
      }
    },

    async fetchNoticesByCategory(tableName) {
      try {
        const response = await axios.get(`http://127.0.0.1:8000/notices/${tableName}`);
        const notices = response.data.map(notice => ({ ...notice, tableName }));

        const monthNames = [
          "JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE",
          "JULY", "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER"
        ];

        const colorMap = {
          kyjs: "#2196F3",
          bksy: "#4CAF50",
          ckc: "#FFC107",
          danqing: "#E91E63",
          jiaoliu: "#9C27B0",
          lantian: "#3F51B5",
          qsxy: "#009688",
          yunfeng: "#FF5722",
        };

        this.defaultEvents = notices.map(notice => {
          const dateObj = new Date(notice.date);
          const monthIndex = dateObj.getMonth();
          const monthName = monthNames[monthIndex];
          const monthEnum = Month[monthName];
          const dayOfMonth = dateObj.getDate();
          const hour = dateObj.getHours();

          return {
            data: {
              title: notice.title,
              color: colorMap[notice.tableName],
              description: notice.content,
              link: notice.link,
            },
            schedule: {
              month: [monthEnum],
              dayOfMonth: [dayOfMonth],
              times: [hour],
              duration: 60,
              durationUnit: "minutes",
            },
          };
        });

        this.loadState();
      } catch (error) {
        console.error(`Error fetching notices for ${tableName}:`, error);
      }
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
}

.calendar-container {
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: space-between;
  flex: 1;
  padding-bottom: 70px; /* 为banner预留空间 */
}

.empty-space {
  margin-top: 60px;
  width: 10%;
  justify-content: left;
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



.bottom-banner {
  position: fixed;
  bottom: 0;
  left: 0;
  width: 100%;
  background-color: #e3f2fd; /* 淡蓝色背景 */
  color: #1e88e5; /* 深蓝色文字 */
  text-align: center;
  padding: 10px 0;
  box-shadow: 0 -2px 10px rgba(0, 0, 0, 0.1);
  font-size: 14px;
}

.footer-content {
  display: flex;
  justify-content: center;
  gap: 20px;
}

.footer-link {
  cursor: pointer;
  color: #1e88e5;
  text-decoration: none;
}

.footer-link:hover {
  text-decoration: underline;
}

.footer-note {
  margin-top: 5px;
  font-size: 12px;
  color: #bac1c5;
}

.chat-container {
  position: fixed;
  bottom: 0;
  width: 100%;
  /* max-width: 600px; */
  background: #f4f4f4;
  border-top: 1px solid #ddd;
}
.chat-window {
  max-height: 300px;
  overflow-y: auto;
  padding: 10px;
}

.chat-message {
  margin-bottom: 10px;
}

.user-message {
  color: #007bff;
  text-align: right;
}
.bot-message {
  color: #444;
  text-align: left;
}

.chat-input-container {
  display: flex;
  align-items: center;
  padding: 10px;
  background: #fff;
  border-top: 1px solid #ddd;
}
.chat-input-container .el-input {
  flex-grow: 1;
  margin-right: 10px;
}
</style>
