local mp_utils = require('mp.utils')

function search_iqdb()
    local name = os.tmpname()
    local handle = io.open(name, 'w')

    mp.osd_message('Downloading results from IQDB...')
    mp_utils.subprocess({args = {
        'curl',
        '-F', 'file=@' .. mp.get_property('path'),
        '-o', name,
        'https://iqdb.org/',
    }})

    mp_utils.subprocess({args = {
        'sed',
        '-i', 's#</head>#<base href="https://iqdb.org"></head>#',
        name}
    })

    mp_utils.subprocess({args = {'firefox', name}})
end

mp.register_script_message('search-iqdb', search_iqdb)
