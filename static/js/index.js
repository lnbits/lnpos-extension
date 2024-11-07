window.app = Vue.createApp({
  el: '#vue',
  mixins: [windowMixin],
  data() {
    return {
      protocol: window.location.protocol,
      location: window.location.hostname,
      filter: '',
      currency: 'USD',
      deviceString: '',
      lnposs: [],
      lnposTable: {
        columns: [
          {
            name: 'title',
            align: 'left',
            label: 'title',
            field: 'title'
          },
          {
            name: 'theId',
            align: 'left',
            label: 'id',
            field: 'id'
          },
          {
            name: 'key',
            align: 'left',
            label: 'key',
            field: 'key'
          },
          {
            name: 'wallet',
            align: 'left',
            label: 'wallet',
            field: 'wallet'
          },
          {
            name: 'currency',
            align: 'left',
            label: 'currency',
            field: 'currency'
          }
        ],
        pagination: {
          rowsPerPage: 10
        }
      },
      settingsDialog: {
        show: false,
        data: {}
      },
      formDialog: {
        show: false,
        data: {}
      }
    }
  },
  methods: {
    cancelLnpos() {
      this.formDialog.show = false
      this.clearFormDialog()
    },
    closeFormDialog() {
      this.clearFormDialog()
      this.formDialog.data = {
        is_unique: false
      }
    },
    sendFormData() {
      if (!this.formDialog.data.profit) {
        this.formDialog.data.profit = 0
      }
      if (this.formDialog.data.id) {
        this.updateLnpos(this.g.user.wallets[0].adminkey, this.formDialog.data)
      } else {
        this.createLnpos(this.g.user.wallets[0].adminkey, this.formDialog.data)
      }
    },

    createLnpos(wallet, data) {
      const updatedData = {}
      for (const property in data) {
        if (data[property]) {
          updatedData[property] = data[property]
        }
      }
      LNbits.api
        .request('POST', '/lnpos/api/v1', wallet, updatedData)
        .then(response => {
          this.lnposs.push(response.data)
          this.formDialog.show = false
          this.clearFormDialog()
        })
        .catch(LNbits.utils.notifyApiError)
    },
    getLnposs() {
      LNbits.api
        .request(
          'GET',
          '/lnpos/api/v1',
          this.g.user.wallets[0].adminkey
        )
        .then(response => {
          if (response.data) {
            this.lnposs = response.data
          }
        })
        .catch(LNbits.utils.notifyApiError)
    },
    getLnpos: lnpos_id => {
      LNbits.api
        .request(
          'GET',
          '/lnpos/api/v1/' + lnpos_id,
          this.g.user.wallets[0].adminkey
        )
        .then(response => {
          localStorage.setItem('lnpos', JSON.stringify(response.data))
          localStorage.setItem('inkey', this.g.user.wallets[0].inkey)
        })
        .catch(LNbits.utils.notifyApiError)
    },
    deleteLnpos(lnposId) {
      LNbits.utils
        .confirmDialog('Are you sure you want to delete this pay link?')
        .onOk(() => {
          LNbits.api
            .request(
              'DELETE',
              '/lnpos/api/v1/' + lnposId,
              this.g.user.wallets[0].adminkey
            )
            .then(response => {
              this.lnposs = _.reject(this.lnposs, obj => {
                return obj.id === lnposId
              })
            })
            .catch(LNbits.utils.notifyApiError)
        })
    },
    openUpdateLnpos(lnposId) {
      const lnpos = _.findWhere(this.lnposs, {
        id: lnposId
      })
      this.formDialog.data = _.clone(lnpos)
      this.formDialog.show = true
    },
    openSettings(lnposId) {
      const lnpos = _.findWhere(this.lnposs, {
        id: lnposId
      })
      this.deviceString = this.protocol + '//' + this.location + '/lnpos/api/v1/lnurl/' + lnpos.id + ',' + lnpos.key + ',' + lnpos.currency
      this.settingsDialog.data = _.clone(lnpos)
      this.settingsDialog.show = true
    },
    updateLnpos(wallet, data) {
      const updatedData = {}
      for (const property in data) {
        if (data[property]) {
          updatedData[property] = data[property]
        }
      }

      LNbits.api
        .request(
          'PUT',
          '/lnpos/api/v1/' + updatedData.id,
          wallet,
          updatedData
        )
        .then(response => {
          this.lnposs = _.reject(this.lnposs, obj => {
            return obj.id === updatedData.id
          })
          this.lnposs.push(response.data)
          this.formDialog.show = false
          this.clearFormDialog()
        })
        .catch(LNbits.utils.notifyApiError)
    },
    clearFormDialog() {
      this.formDialog.data = {
        lnurl_toggle: false,
        show_message: false,
        show_ack: false,
        show_price: 'None',
        title: ''
      }
    },
    exportCSV() {
      LNbits.utils.exportCSV(this.lnposTable.columns, this.lnposs)
    }
  },
  created() {
    this.getLnposs()
    LNbits.api
      .request('GET', '/api/v1/currencies')
      .then(response => {
        this.currency = ['sat', 'USD', ...response.data]
      })
      .catch(LNbits.utils.notifyApiError)
  }
})
