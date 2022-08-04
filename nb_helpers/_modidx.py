# Autogenerated by nbdev

d = { 'settings': { 'audience': 'Developers',
                'author': 'Thomas Capelle',
                'author_email': 'tcapelle@wandb.com',
                'branch': 'main',
                'console_scripts': 'nb_helpers.clean_nbs=nb_helpers.clean:clean_nbs\n'
                                   'nb_helpers.run_nbs=nb_helpers.run:run_nbs\n'
                                   'nb_helpers.summary_nbs=nb_helpers.wandb:summary_nbs\n'
                                   'nb_helpers.fix_nbs=nb_helpers.wandb:fix_nbs\n'
                                   'nb_helpers.filter_nbs=nb_helpers.wandb:filter_nbs',
                'copyright': 'wandb',
                'custom_sidebar': 'False',
                'description': 'A set of tools for nb handling',
                'doc_baseurl': '/nb_helpers/',
                'doc_host': 'https://wandb.github.io',
                'doc_path': '_docs',
                'git_url': 'https://github.com/wandb/nb_helpers/tree/main/',
                'host': 'github',
                'keywords': 'jupyter notebook',
                'language': 'English',
                'lib_name': 'nb_helpers',
                'lib_path': 'nb_helpers',
                'license': 'mit',
                'min_python': '3.7',
                'nbs_path': 'nbs',
                'requirements': 'rich fastcore ipython execnb ghapi GitPython',
                'status': '4',
                'title': 'nb_helpers',
                'tst_flags': 'slow',
                'user': 'wandb',
                'version': '0.2.8'},
  'syms': { 'nb_helpers.actions': { 'nb_helpers.actions.after_pr_colab_link': 'https://wandb.github.io/nb_helpers/actions.html#after_pr_colab_link',
                                    'nb_helpers.actions.create_comment_body': 'https://wandb.github.io/nb_helpers/actions.html#create_comment_body',
                                    'nb_helpers.actions.create_issue_nb_fail': 'https://wandb.github.io/nb_helpers/actions.html#create_issue_nb_fail',
                                    'nb_helpers.actions.get_colab_url2md': 'https://wandb.github.io/nb_helpers/actions.html#get_colab_url2md'},
            'nb_helpers.clean': { 'nb_helpers.clean.CLEAN_TABLE': 'https://wandb.github.io/nb_helpers/clean.html#clean_table',
                                  'nb_helpers.clean.CONSOLE': 'https://wandb.github.io/nb_helpers/clean.html#console',
                                  'nb_helpers.clean.cell_metadata_keep': 'https://wandb.github.io/nb_helpers/clean.html#cell_metadata_keep',
                                  'nb_helpers.clean.clean_all': 'https://wandb.github.io/nb_helpers/clean.html#clean_all',
                                  'nb_helpers.clean.clean_cell': 'https://wandb.github.io/nb_helpers/clean.html#clean_cell',
                                  'nb_helpers.clean.clean_cell_output': 'https://wandb.github.io/nb_helpers/clean.html#clean_cell_output',
                                  'nb_helpers.clean.clean_nb': 'https://wandb.github.io/nb_helpers/clean.html#clean_nb',
                                  'nb_helpers.clean.clean_nbs': 'https://wandb.github.io/nb_helpers/clean.html#clean_nbs',
                                  'nb_helpers.clean.clean_one': 'https://wandb.github.io/nb_helpers/clean.html#clean_one',
                                  'nb_helpers.clean.clean_output_data_vnd': 'https://wandb.github.io/nb_helpers/clean.html#clean_output_data_vnd',
                                  'nb_helpers.clean.colab_json': 'https://wandb.github.io/nb_helpers/clean.html#colab_json',
                                  'nb_helpers.clean.nb_metadata_keep': 'https://wandb.github.io/nb_helpers/clean.html#nb_metadata_keep',
                                  'nb_helpers.clean.rm_execution_count': 'https://wandb.github.io/nb_helpers/clean.html#rm_execution_count'},
            'nb_helpers.colab': { 'nb_helpers.colab.add_colab_badge': 'https://wandb.github.io/nb_helpers/colab.html#add_colab_badge',
                                  'nb_helpers.colab.add_colab_metadata': 'https://wandb.github.io/nb_helpers/colab.html#add_colab_metadata',
                                  'nb_helpers.colab.create_colab_badge_cell': 'https://wandb.github.io/nb_helpers/colab.html#create_colab_badge_cell',
                                  'nb_helpers.colab.get_colab_url': 'https://wandb.github.io/nb_helpers/colab.html#get_colab_url',
                                  'nb_helpers.colab.has_colab_badge': 'https://wandb.github.io/nb_helpers/colab.html#has_colab_badge'},
            'nb_helpers.run': { 'nb_helpers.run.CaptureShell.prettytb': 'https://wandb.github.io/nb_helpers/run.html#captureshell.prettytb',
                                'nb_helpers.run.exec_nb': 'https://wandb.github.io/nb_helpers/run.html#exec_nb',
                                'nb_helpers.run.run_nbs': 'https://wandb.github.io/nb_helpers/run.html#run_nbs',
                                'nb_helpers.run.run_one': 'https://wandb.github.io/nb_helpers/run.html#run_one'},
            'nb_helpers.utils': { 'nb_helpers.utils.CellType': 'https://wandb.github.io/nb_helpers/utils.html#celltype',
                                  'nb_helpers.utils.LOGFORMAT': 'https://wandb.github.io/nb_helpers/utils.html#logformat',
                                  'nb_helpers.utils.LOGFORMAT_RICH': 'https://wandb.github.io/nb_helpers/utils.html#logformat_rich',
                                  'nb_helpers.utils.RichLogger': 'https://wandb.github.io/nb_helpers/utils.html#richlogger',
                                  'nb_helpers.utils.RichLogger.create_github_issue': 'https://wandb.github.io/nb_helpers/utils.html#richlogger.create_github_issue',
                                  'nb_helpers.utils.RichLogger.error': 'https://wandb.github.io/nb_helpers/utils.html#richlogger.error',
                                  'nb_helpers.utils.RichLogger.exception': 'https://wandb.github.io/nb_helpers/utils.html#richlogger.exception',
                                  'nb_helpers.utils.RichLogger.info': 'https://wandb.github.io/nb_helpers/utils.html#richlogger.info',
                                  'nb_helpers.utils.RichLogger.to_csv': 'https://wandb.github.io/nb_helpers/utils.html#richlogger.to_csv',
                                  'nb_helpers.utils.RichLogger.to_md': 'https://wandb.github.io/nb_helpers/utils.html#richlogger.to_md',
                                  'nb_helpers.utils.RichLogger.to_table': 'https://wandb.github.io/nb_helpers/utils.html#richlogger.to_table',
                                  'nb_helpers.utils.RichLogger.warning': 'https://wandb.github.io/nb_helpers/utils.html#richlogger.warning',
                                  'nb_helpers.utils.RichLogger.writerow': 'https://wandb.github.io/nb_helpers/utils.html#richlogger.writerow',
                                  'nb_helpers.utils.RichLogger.writerow_incolor': 'https://wandb.github.io/nb_helpers/utils.html#richlogger.writerow_incolor',
                                  'nb_helpers.utils.STATUS': 'https://wandb.github.io/nb_helpers/utils.html#status',
                                  'nb_helpers.utils.create_table': 'https://wandb.github.io/nb_helpers/utils.html#create_table',
                                  'nb_helpers.utils.csv_to_md': 'https://wandb.github.io/nb_helpers/utils.html#csv_to_md',
                                  'nb_helpers.utils.detect_imported_libs': 'https://wandb.github.io/nb_helpers/utils.html#detect_imported_libs',
                                  'nb_helpers.utils.extract_libs': 'https://wandb.github.io/nb_helpers/utils.html#extract_libs',
                                  'nb_helpers.utils.find_nbs': 'https://wandb.github.io/nb_helpers/utils.html#find_nbs',
                                  'nb_helpers.utils.git_current_branch': 'https://wandb.github.io/nb_helpers/utils.html#git_current_branch',
                                  'nb_helpers.utils.git_last_commit': 'https://wandb.github.io/nb_helpers/utils.html#git_last_commit',
                                  'nb_helpers.utils.git_local_repo': 'https://wandb.github.io/nb_helpers/utils.html#git_local_repo',
                                  'nb_helpers.utils.git_main_name': 'https://wandb.github.io/nb_helpers/utils.html#git_main_name',
                                  'nb_helpers.utils.git_origin_repo': 'https://wandb.github.io/nb_helpers/utils.html#git_origin_repo',
                                  'nb_helpers.utils.is_nb': 'https://wandb.github.io/nb_helpers/utils.html#is_nb',
                                  'nb_helpers.utils.print_output': 'https://wandb.github.io/nb_helpers/utils.html#print_output',
                                  'nb_helpers.utils.remove_rich_format': 'https://wandb.github.io/nb_helpers/utils.html#remove_rich_format',
                                  'nb_helpers.utils.search_cell': 'https://wandb.github.io/nb_helpers/utils.html#search_cell',
                                  'nb_helpers.utils.search_cells': 'https://wandb.github.io/nb_helpers/utils.html#search_cells',
                                  'nb_helpers.utils.search_string_in_nb': 'https://wandb.github.io/nb_helpers/utils.html#search_string_in_nb',
                                  'nb_helpers.utils.today': 'https://wandb.github.io/nb_helpers/utils.html#today'},
            'nb_helpers.wandb': { 'nb_helpers.wandb.PYTHON_LIBS': 'https://wandb.github.io/nb_helpers/wandb.html#python_libs',
                                  'nb_helpers.wandb.WANDB_FEATURES': 'https://wandb.github.io/nb_helpers/wandb.html#wandb_features',
                                  'nb_helpers.wandb.filter_nbs': 'https://wandb.github.io/nb_helpers/wandb.html#filter_nbs',
                                  'nb_helpers.wandb.fix_nbs': 'https://wandb.github.io/nb_helpers/wandb.html#fix_nbs',
                                  'nb_helpers.wandb.get_wandb_tracker': 'https://wandb.github.io/nb_helpers/wandb.html#get_wandb_tracker',
                                  'nb_helpers.wandb.search_code': 'https://wandb.github.io/nb_helpers/wandb.html#search_code',
                                  'nb_helpers.wandb.summary_nbs': 'https://wandb.github.io/nb_helpers/wandb.html#summary_nbs'}}}