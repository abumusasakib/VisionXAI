import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:vision_xai/l10n/localization_extension.dart';
import 'package:vision_xai/settings/settings_cubit.dart';
import 'package:vision_xai/settings/settings_state.dart'; // Importing the cubit

class IPSettings extends StatelessWidget {
  IPSettings({super.key});

  final TextEditingController ipController = TextEditingController();
  final TextEditingController portController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return BlocProvider(
      create: (_) => SettingsCubit()..loadIpAndPort(),
      child: Scaffold(
        appBar: AppBar(
          title: Text(context.tr.settingsScreenTitle),
        ),
        body: SafeArea(
          child: SingleChildScrollView(
            padding: EdgeInsets.all(20),
            child: BlocListener<SettingsCubit, SettingsState>(
              listenWhen: (previous, current) =>
                  previous.ip != current.ip || previous.port != current.port,
              listener: (context, state) {
                // Update controllers when the state changes
                ipController.text = state.ip;
                portController.text = state.port;
              },
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  TextField(
                    controller: ipController,
                    keyboardType: TextInputType.text,
                    decoration: InputDecoration(
                      labelText: context.tr.ip,
                    ),
                  ),
                  SizedBox(
                    height: 10,
                  ),
                  TextField(
                    controller: portController,
                    keyboardType: TextInputType.number,
                    decoration: InputDecoration(
                      labelText: context.tr.port,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
        floatingActionButton: FloatingActionButton.extended(
          onPressed: () {
            String ip = ipController.text;
            String port = portController.text;

            if (ip.isNotEmpty && port.isNotEmpty) {
              context.read<SettingsCubit>().updateIpAndPort(ip, port);
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(
                  backgroundColor: Colors.green.shade600,
                  content: Text(
                    context.tr.ipPortUpdated,
                    style: TextStyle(
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
              );
            } else {
              ScaffoldMessenger.of(context).showSnackBar(
                SnackBar(content: Text(context.tr.enterIpAndPort)),
              );
              Navigator.of(context).pop();
            }
          },
          elevation: 0,
          icon: Icon(Icons.file_upload_outlined),
          label: Text(context.tr.updateIp),
        ),
      ),
    );
  }
}
