<template>
    <div>
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
            <strong class="ds-ev-title" style="word-wrap: break-word">{{
              details.title
            }}</strong>
          </div>
        </template>
      </ds-calendar-app>
    </div>
  </template>
  
  <script>
  import { Calendar, Month } from "dayspan";
  import axios from "axios";
  
  export default {
    name: "CalendarView",
    data: () => ({
      storeKey: "dayspanState",
      calendar: Calendar.weeks(),
      readOnly: true,
      defaultEvents: [],
      tableNames: ["kyjs", "bksy", "ckc", "danqing", "jiaoliu", "lantian", "qsxy", "yunfeng"],
    }),
    mounted() {
      window.app = this.$refs.app;
      this.fetchNotices();
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
          console.log(e);
        }
  
        state.events = this.defaultEvents;
  
        state.events.forEach((ev) => {
          let defaults = this.$dayspan.getDefaultEventDetails();
          ev.data = { ...defaults, ...ev.data };
        });
  
        this.$refs.app.setState(state);
      },
      async fetchNotices() {
        try {
          const allNotices = [];
          for (const tableName of this.tableNames) {
            const response = await axios.get(`http://127.0.0.1:8000/notices/${tableName}`);
            allNotices.push(...response.data);
          }
  
          const monthNames = [
            "JANUARY", "FEBRUARY", "MARCH", "APRIL", "MAY", "JUNE",
            "JULY", "AUGUST", "SEPTEMBER", "OCTOBER", "NOVEMBER", "DECEMBER"
          ];
  
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
                color: "#2196F3",
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
          console.error("Error fetching notices:", error);
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
    color: #90a4ae;
  }
  
  .main-content {
    flex: 1;
    margin-top: 60px;
    margin-right: 20px;
    margin-left: 20px;
  }
  </style>
  