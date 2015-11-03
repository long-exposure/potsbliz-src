$(document).ready(function () {

	$('#li-speeddial').after('<li><a href="#tabs-sip">SIP account</a></li>');
	$('#tabs-speeddial').after('<div id="tabs-sip"><div id="SipAccountContainer"></div></div>');

    $('#SipAccountContainer').jtable({
        jqueryuiTheme: true,
        actions: {
            listAction:   '/plugin/sip/sip_account.py/list',
            updateAction: '/plugin/sip/sip_account.py/update'
        },
        fields: {
            id: {
                key: true,
                list: false
            },
            identity: {
                title: 'Identity',
                width: '50%'
            },
            proxy: {
                title: 'Proxy',
                width: '50%'
            },
            password: {
                title: 'Password',
                list: false
            },
        },
        rowUpdated: (function (event, data) {
        	alert('Reboot required!');
        }),
    });

    $('#SipAccountContainer').jtable('load');
});
