Vue.component('facet-modal', {
    props: ['facet_key', 'facet_title', 'list'],

    template: '<div class="modal fade facet-modal" id="facetModal-test" tabindex="-1" role="dialog"  aria-hidden="true">\n' +
        '        <div class="modal-dialog modal-lg" role="document">\n' +
        '            <div class="modal-content">\n' +
        '                <div class="modal-header">\n' +
        '                    <h5 class="modal-title">{{ facet_title }}</h5>\n' +
        '                    <button type="button" class="close" data-dismiss="modal" aria-label="Close">\n' +
        '                        <span aria-hidden="true">&times;</span>\n' +
        '                    </button>\n' +
        '                </div>\n' +
        '                <div class="modal-body">\n' +
        '                    <div class="in-facet-search">\n' +
        '                        <input class="form-control form-control-sm in-facet-search-input">\n' +
        '                    </div>\n' +
        '                    <div class="pt-2 facet-modal-options">\n' +
        '                        <div v-for="checkedOption in list" class="form-check w-100" data-value="test">\n' +
        '                            <input class="form-check-input" type="checkbox" :value="checkedOption" :key="checkedOption.value" name="test" v-model="list" checked>\n' +
        '                            <label class="form-check-label w-100">\n' +
        '                                <div class="facet-submenu-item">\n' +
        '                                    <div class="d-inline-block text-truncate">{{ checkedOption.text }}</div>\n' +
        '                                    <div><span class="badge badge-pill badge-secondary">test</span></div>\n' +
        '                                </div>\n' +
        '                            </label>\n' +
        '                        </div>\n' +
        '\n' +
        '                        <hr>\n' +
        '\n' +
        '                        <div v-for="option in options" class="form-check w-100" data-value="test">\n' +
        '                            <input class="form-check-input" type="checkbox" :value="option" :key="option.value" name="test" v-model="list">\n' +
        '                            <label class="form-check-label w-100">\n' +
        '                                <div class="facet-submenu-item">\n' +
        '                                    <div class="d-inline-block text-truncate">{{ option.text }}</div>\n' +
        '                                    <div><span class="badge badge-pill badge-secondary">test</span></div>\n' +
        '                                </div>\n' +
        '                            </label>\n' +
        '                        </div>\n' +
        '                    </div>\n' +
        '                </div>\n' +
        '                <div class="modal-footer">\n' +
        '                    <button type="button" class="btn btn-secondary" data-dismiss="modal">Close</button>\n' +
        '                    <button type="button" class="btn btn-primary">Save changes</button>\n' +
        '                </div>\n' +
        '            </div>\n' +
        '        </div>\n' +
        '    </div>',

    data() {
        return {
            options: [
                {text: 'Czechia', value: 'cz'},
                {text: 'Slovakia', value: 'sk'},
                {text: 'Netherlands', value: 'nl'}
            ],

        }
    },
    model: {
        prop: 'list',
        event: 'listchange'
    },
    computed: {
        listLocal: {
            get: function() {
                return this.list
            },
            set: function(value) {
                this.$emit('listchange', value)
            }
        }
    }
});

var vue = new Vue({
    el: '#vue',
    data: {
        list: []
    },
});