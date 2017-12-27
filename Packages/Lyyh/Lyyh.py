import sublime, sublime_plugin
import os,re,threading
import subprocess
import pyodbc
import codecs
# import Sybase

basedir = 'D:/lyyh/'
DSN = "DSN=8100ceshi;PWD=qz8100"
DB_LIST=["LyVsMj","cbly220.1","1100","5100","2100","mjmf_4201","mjceshi","mjcs80","8100ceshi","7100","7500","szceshi","szbs_4101","cbly220.4"]
DSN_MAP={
	"8100":"DSN=8100ceshi;PWD=qz8100",
	"2100":"DSN=2100",
	"5100":"DSN=5100;PWD=5100cs",
	"cbly220.1":"DSN=cbly220.1;PWD=cbly2015"
}
# dir(DSN_MAP.keys())
# print(DSN_MAP.keys())

def open_procfile(window, procnaOrPrcscd, lyormj):
	if os.path.isfile(basedir+"core/"+lyormj+"_proc/" + procnaOrPrcscd +'.sql'):
		window.open_file(basedir+"core/"+lyormj+"_proc/" + procnaOrPrcscd +'.sql')
	else:
		prcscd = procnaOrPrcscd.lower()
		if prcscd in get_setting("prcs"):
			procna = get_setting("prcs")[prcscd]
			open_procfile(window, procna, lyormj)

class dbhandler(threading.Thread): #在ui线程外连接db
	def __init__(self):
		threading.Thread.__init__(self)
		self.thread_stop = False

	def run(self):
		global CNNCTN
		if DSN != '':
			print(DSN)
			CNNCTN=pyodbc.connect(DSN)
			sublime.message_dialog(DSN+" 连接成功")
			CNNCTN.autocommit = True

class ProcCommand(sublime_plugin.WindowCommand):
	def run(self,lyormj):
		view = self.window.active_view()
		sels = view.sel()
		for sel in sels:
			open_procfile(self.window,view.substr(sel),lyormj)


class ProcByPrcsCommand(sublime_plugin.WindowCommand):
	def run(self,lyormj):
		view = self.window.active_view()
		prcscd = view.substr(view.sel()[0])
		def on_submit(text):
			open_procfile(self.window,text,lyormj)

		sublime.active_window().show_input_panel(lyormj+" prcscd",prcscd,on_submit,None,None)


class GentCommand(sublime_plugin.WindowCommand):
	def run(self):
		view = self.window.active_view()
		sels = view.sel()
		sel = sels[0]
		tablefile = basedir+"table/" + view.substr(sels[0])+".sql"
		if os.path.exists(tablefile):
			self.window.open_file(tablefile)

class SwitchdbCommand(sublime_plugin.WindowCommand):
	def run(self):
		def on_dbselected(idx):
			global DSN
			DSN=DSN_MAP[list(DSN_MAP.keys())[idx]]
			dbhandler().start()
		sublime.active_window().show_quick_panel(list(DSN_MAP.keys()), on_dbselected)

dbhandler().start()

class DictCommand(sublime_plugin.WindowCommand):
	def run(self):
		view = self.window.active_view()
		sels = view.sel()
		cur = CNNCTN.cursor()
		cur.execute("sp_dict " + view.substr(sels[0]))
		result = ''
		while True:
			row = cur.fetchone()
			if (not row):
				break
			result += "%s | %s | %s | %s\n" % (row[0], row[1], row[2], row[3])

		if(sublime.ok_cancel_dialog(result)):
			sublime.set_clipboard(result)

		print(result)
		cur.close()

class DateCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		global CNNCTN
		cur = CNNCTN.cursor()
		cur.execute("SELECT convert(CHAR,syscdt,112) FROM knp_sysc WHERE sysctp = \'date\' AND sysccd = \'sysd\'")
		row = cur.fetchone()
		result = row[0]
		if(result!=''):sublime.message_dialog(result)
		print(result)
		cur.close()

class FindDeclareCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		view = self.view
		sels = view.sel()
		name = view.substr(sels[0])
		# pattern = re.compile(r'declare\s+%s' % name)
		# match = pattern.match('declare  run')
		# if match:
		# 	print('true')
		# if name[0] != '@':
		# 	name = '@'+name
		# declare_region = view.find(r'declare(\s+)%s' % name,0)
		declare_line = view.line(view.find(r'%s' % name,0))
		line_bg = view.rowcol(declare_line.begin())
		# print(view.substr(0))
		# sublime.message_dialog(str(line_bg[0]) + ' ' + view.substr(declare_line).strip())
		if(sublime.ok_cancel_dialog(str(line_bg[0]) + ' ' + view.substr(declare_line).strip())):
			view.show(declare_line)

		# print(view.substr(declare_line))

class DiffCommand(sublime_plugin.WindowCommand):
	def run(self,lyormj):
		my_server=""
		def on_done(idx):
			if idx >= 1:
				my_server=DB_LIST[idx]
				left = get_setting('left')
				right = get_setting('right')
				view = self.window.active_view()
				sels = view.sel()
				for sel in sels:
					procname=view.substr(sel)
					if procname == '':
						procname = os.path.basename(view.file_name()).split('.')[0]
					if(left['type'] == 'local'):
						left['dir'] = "core/"+lyormj+"_proc"
						leftfile=basedir+left['dir']+'/'+procname+'.sql'
					elif(left['type'] == 'server'):
						proc_cmd = basedir+'diff_proc.bat '+left['dir']+' '+procname
						os.system(proc_cmd)
						leftfile='C:/Temp/'+left['dir']+'/'+procname+'.sql'

					if(right['type'] == 'local'):
						rightfile=basedir+right['dir']+'/'+procname+'.sql'
					elif(right['type'] == 'server'):
						proc_cmd = basedir+'diff_proc.bat '+right['dir']+' '+procname
						os.system(proc_cmd)
						rightfile='C:/Temp/'+right['dir']+'/'+procname+'.sql'
					elif(right['type'] == 'panel'):
						proc_cmd = basedir+'diff_proc.bat '+my_server+' '+procname
						print(proc_cmd)
						os.system(proc_cmd)
						rightfile='C:/Temp/'+my_server+'/'+procname+'.sql'
					diff_cmd = basedir+'by.bat '+leftfile+" "+rightfile
					print(diff_cmd)
					os.system(diff_cmd)
			elif idx == 0:
				view = self.window.active_view()
				sels = view.sel()
				for sel in sels:
					procname=view.substr(sel)
					if procname == '':
						procname = os.path.basename(view.file_name()).split('.')[0]
					leftfile=basedir+'core/ly_proc/'+procname+'.sql'
					rightfile=basedir+'core/mj_proc/'+procname+'.sql'
					diff_cmd = basedir+'by.bat '+leftfile+" "+rightfile
					print(diff_cmd)
					os.system(diff_cmd)

		sublime.active_window().show_quick_panel(DB_LIST, on_done)

# %PROC_FLIE% %LOCAL_FLIE%

def get_setting(key, default_value=None):
	settings = sublime.load_settings('Lyyh.sublime-settings')
	return settings.get(key, default_value)

class DatatypeCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		iview = self.view
		datatype = iview.substr(iview.sel()[0])
		if datatype.find("_"):
			datatype = datatype.split('_')[-1]
		msg = ''
		csvfile = codecs.open("C://Users//Administrator//PycharmProjects//lyyh//dict.json","r","utf-8")
		for line in csvfile.readlines():
			if re.search(datatype,line):
				msg+=line
		if(datatype!=''):sublime.message_dialog(msg)

class ItemCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		iview = self.view
		item = iview.substr(iview.sel()[0])
		msg = ''
		csvfile = codecs.open("D://lyyh//other//itemdtit.csv","r","utf-8")
		for line in csvfile.readlines():
			if re.search('^'+item+'\d*,',line):
				msg+=line
		if(item!=''):sublime.message_dialog(msg)

class DtitCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		iview = self.view
		dtit = iview.substr(iview.sel()[0])
		msg = ''
		csvfile = codecs.open("D://lyyh//other//itemdtit.csv","r","utf-8")
		for line in csvfile.readlines():
			if re.search(','+dtit+',',line):
				msg+=line
		if(dtit!=''):
			sublime.message_dialog(msg)
			sublime.set_clipboard(msg)

class PopupListener(sublime_plugin.ViewEventListener):
	print("PopupListener load")
	itemdtit = codecs.open("D://lyyh//other//itemdtit.csv","r","utf-8")
	def on_hover(self, point, hover_zone):
		if(hover_zone==sublime.HOVER_TEXT):
			# print(sublime.COOPERATE_WITH_AUTO_COMPLETE) # 2
			# print(sublime.HIDE_ON_MOUSE_MOVE) # 4
			# print(sublime.HIDE_ON_MOUSE_MOVE_AWAY) # 8
			# print(sublime.COOPERATE_WITH_AUTO_COMPLETE|sublime.HIDE_ON_MOUSE_MOVE) # 6
			view=self.view
			dtit=view.substr(view.word(point))
			find=False
			html = """
				<body id=show-dtit>
					<a href="%s">%s</a>
				</body>
				"""

			if re.match(r'^\d{6}$',dtit):
				for line in self.itemdtit.readlines():
					if re.search(','+dtit+',',line):
						view.show_popup(html % (line,line),sublime.HIDE_ON_MOUSE_MOVE_AWAY,point,max_width=2000,on_navigate=lambda x: copy(self.view, x))
						find=True
			self.itemdtit.seek(0) # 两次readlines之间需加seek(0)

			if find==False and re.match(r'^\d{4,12}$',dtit):
				for line in self.itemdtit.readlines():
					if re.search('^'+dtit+',',line): #itemcd
						view.show_popup(html % (line,line),sublime.HIDE_ON_MOUSE_MOVE_AWAY,point,max_width=2000,on_navigate=lambda x: copy(self.view, x))
						find=True
						break
			self.itemdtit.seek(0) # 两次readlines之间需加seek(0)

def copy(view, text):
	sublime.set_clipboard(text)
	view.hide_popup()
	sublime.status_message(text)

class DelBackslashCommand(sublime_plugin.TextCommand):
	def run(self, edit):
		iview = self.view
		# print(len(iview.sel())) #至少是1
		selected = False
		for iregion in reversed(iview.sel()):
			if not iregion.empty():
				selected = True
				pckgda = iview.substr(iregion)
				pckgda = re.sub(r'(?<=\|)wndwda=','',pckgda) # 删除 wndwda=
				pckgda = re.sub(r'\\\|','|',pckgda) # \=改为=
				pckgda = re.sub(r'\\\=','=',pckgda) # \|改为|
				pckgda = re.sub(r'\|\|','|',pckgda) # ||改为|
				pckgda = re.sub(r'(?<=\|)\w*\=\|','',pckgda) # 删除空值
				pckgda = re.sub(r'(?<=\|)sessid=\d*\|','',pckgda) # 删除 sessid=11710|
				pckgda = re.sub(r'\|1:=\|2:','|\n1:=|2:',pckgda) # 1:=|2:前加换行
				# print(pckgda)
				iview.replace(edit, iregion, pckgda)

		# if not selected:
		# 	backslash = iview.find_all(r'\\(?=\|)|\\(?=\=)')
		# 	# backslash.reverse()
		# 	for r in backslash:
		# 		iview.erase(edit, r)

		# 	backslash = iview.find_all(r'(?<=\|)\w*\=\|')
		# 	for r in backslash:
		# 		iview.erase(edit, r)
