import json

languages_var = ["Arabic", "English", "French", "German", "Italian", "Kurdish", "Latin", "Romanian", "Russian", "Spanish", "Swedish", "Turkish"]


settings_json = json.dumps([
	{"type": "title",
	"title": "Languages"},
	{"type": "scrolloptions",
	"title": "Search-Language: ",
	"section": "languages",
	"key": "learnlanguage",
	"desc": "e.g. the language you want to learn: ",
	"options": languages_var},
	{"type": "scrolloptions",
	"title": "Return-Language (1): ",
	"section": "languages",
	"key": "motherlanguage",
	"desc": "e.g. your motherlanguage: ",
	"options": languages_var},
	{"type": "scrolloptions",
	"title": "Return-Language (2): ",
	"section": "languages",
	"key": "returnlanguage",
	"desc": "default 'English': ",
	"options": languages_var},
	{"type": "title",
	"title": "Backups"},
	{"type": "path",
	"title": "Path of your backup-file",
	"section": "languages",
	"key": "backuppath",
	"desc": "Path of your backup-file (default ../backups/voctrainer/)"},
	{"type": "bool",
	"title": "Backup your dictionary",
	"section": "languages",
	"key": "makebackup",
	"values": ["no", "yes"]}
	])