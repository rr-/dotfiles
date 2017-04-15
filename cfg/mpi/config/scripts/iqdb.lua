local mp_utils = require('mp.utils')

function search_iqdb()
    local source = mp.get_property('path')
    local target1 = os.tmpname()
    local target2 = os.tmpname()
    local handle = io.open(target1, 'w')

    mp.osd_message('Downloading results from IQDB...')

    file = io.open(target1, 'w')
    file:write('<script>')
    file:write('window.setTimeout(() => window.location.reload(1), 1000);')
    file:write('</script>');
    file:write('<style type="text/css">img { max-width: 200px; max-height: 200px; }</style>');
    file:write('<p>Querying...</p>')
    file:write('<img src="' .. source .. '"/>')
    file:close()

    mp_utils.subprocess({args = {'firefox', target1}})

    mp_utils.subprocess_detached({args = {
        'sh',
        '-c',
        'curl -F "file=@' .. source .. '" -o' .. target2 .. ' https://iqdb.org/ && ' ..
        'sed -i "s#</head>#<base href="https://iqdb.org"></head>#" ' .. target2 .. ' && ' ..
        'sed -i "s#<body>#<body><img style=\'max-width:200px;max-height:200px\' src=\'file://' .. source .. '\'/>#" ' .. target2 .. ' && ' ..
        'mv ' .. target2 .. ' ' .. target1,
    }})
end

mp.register_script_message('search-iqdb', search_iqdb)
