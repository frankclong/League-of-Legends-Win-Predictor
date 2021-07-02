from sklearn.model_selection import train_test_split
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.ensemble import RandomForestClassifier	
from sklearn.metrics import mean_absolute_error
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
import pandas as pd
from xgboost import XGBClassifier
from xgboost import XGBRegressor

# Create model
def main():
	# Column names
	columns = ["Date", "GameLength", "K","D","A","CS","CSpm","GoldDiff","GoldDiffpm","PrevWL","NumFriends","Mood", "Fatigue", "Time", "TimeVal", "Role","WinLoss"]
	col_to_drop = ["Date", "K","D","A","CS","GoldDiff","Time","WinLoss"]
	num_col = ["GameLength","CSpm","GoldDiffpm","PrevWL","NumFriends","Mood", "Fatigue", "TimeVal"]
	# Read data
	file_path = "./loldata.csv"
	game_data = pd.read_csv(file_path, skiprows = [0])
	game_data.columns = columns

	# Process data
	# Calculate KDA (add 0.001 to deaths in case of 0 deaths) 
	game_data["KDA"] =(game_data["K"]+game_data["A"])/(game_data["D"] + 0.001)

	# Drop unimportant columns 
	result = game_data["WinLoss"]
	game_data = game_data.drop(col_to_drop,axis = 1)

	# Fill in missing values
	imputer = SimpleImputer(strategy = 'median')
	imputed_num_cols = pd.DataFrame(imputer.fit_transform(game_data[num_col]))
	imputed_num_cols.columns = num_col
	game_data = pd.concat([imputed_num_cols, game_data['Role']],axis = 1,sort=False)

	# Apply OneHotEncoder on role column (or use get_dummies)
#	OH_encoder = OneHotEncoder(handle_unknown='ignore', sparse=False)
#	OH_cols = ['Role']
#	preprocessor = ColumnTransformer(transformers = [('cat',OH_encoder, OH_cols)])
	game_data = pd.get_dummies(game_data)

	# Create model
	# Random Forest
	#model = RandomForestClassifier(n_estimators = 100, random_state = 0)
	# XGBoost
	#my_model = XGBRegressor(n_estimators=500)
	# model = XGBClassifier(scale_pos_weight=1,
    #                   learning_rate=0.01,  
    #                   colsample_bytree = 0.4,
    #                   subsample = 0.8,
    #                   objective='binary:logistic', 
    #                   n_estimators=1000, 
    #                   reg_alpha = 0.3,
    #                   max_depth=4, 
    #                   gamma=10,
	# 				  eval_metric = "auc",
	# 				  use_label_encoder = False)
	model = XGBClassifier(learning_rate=0.01,  
                      n_estimators=1000, 
					  eval_metric = "error",
					  use_label_encoder = False)

	my_pipeline = Pipeline(steps=[
#		('preprocessor', preprocessor),
		('model', model)
		])

	def validate():
		# Validate model
		## Single validation
		game_data_train, game_data_valid, result_train, result_valid = train_test_split(game_data, result,train_size=0.8,random_state = 0)
		#model.fit(game_data_train, result_train)
		model.fit(game_data_train, result_train, 
             early_stopping_rounds=10, 
             eval_set=[(game_data_valid, result_valid)], 
             verbose=False)
		preds = model.predict(game_data_valid)
		print(list(preds))
		print(list(result_valid))
		error = mean_absolute_error(preds, result_valid)
		print("Single-Validation:", error)

		## Cross-validation
		scores = -1 * cross_val_score(model, game_data, result, cv = 5, scoring = 'neg_mean_absolute_error')
		print("Cross-validation:", scores.mean())

	def predict():
		user_input = ['1']
		my_pipeline.fit(game_data, result)
		pred = my_pipeline.predict(user_input)
		print(pred)

	def analyze():
		# Permutation Importance
		from eli5.sklearn import PermutationImportance
		import eli5
		game_data_train, game_data_valid, result_train, result_valid = train_test_split(game_data, result,train_size=0.67, random_state = 0)
		#my_pipeline.fit(game_data_train, result_train)
		model.fit(game_data_train, result_train, 
             early_stopping_rounds=10, 
             eval_set=[(game_data_valid, result_valid)], 
             verbose=False)
		perm = PermutationImportance(model, random_state=1).fit(game_data_valid, result_valid)

		exp = eli5.explain_weights(perm, feature_names = game_data_valid.columns.tolist())
		print(exp.feature_importances)
		#f = open('perms.html','w',encoding='utf-8')
		#f.write(eli5.explain_weights(perm, feature_names = game_data_valid.columns.tolist()))

	validate()
	analyze()

if __name__ == "__main__":
	main()
	
